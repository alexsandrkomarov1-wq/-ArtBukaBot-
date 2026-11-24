from __future__ import annotations

import json
import os
import secrets
import hashlib
from datetime import timezone
from contextlib import asynccontextmanager
from pathlib import Path

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import build_engine, build_session_factory, session_dependency, verify_migrations_current
from .cloud_archive_api import build_archive_router
from .google_drive_oauth import build_google_drive_router
from .models import AuditEvent, AuthSession, LoginAttempt, Person, RelationshipRecord, SystemState, User, utc_now
from .navigation import build_navigation
from .schemas import (
    BootstrapCreate, LoginRequest, PasswordChange, PersonCreate, PersonRead, PersonUpdate,
    RelationshipCreate, RelationshipRead, SessionRead, TokenRead,
    UserCreate, UserRead, UserUpdate,
)
from .security import (
    ACCESS_TOKEN_SECONDS, create_access_token, decode_access_token,
    hash_password, verify_password,
)


def create_app(
    database_url: str | None = None,
    jwt_secret: str | None = None,
    bootstrap_token: str | None = None,
    media_root: str | Path | None = None,
) -> FastAPI:
    engine = build_engine(database_url)
    session_factory = build_session_factory(engine)
    configured_jwt_secret = jwt_secret if jwt_secret is not None else os.getenv("CORE_JWT_SECRET", "")
    if len(configured_jwt_secret) < 32:
        configured_jwt_secret = ""
    configured_bootstrap_token = (
        bootstrap_token if bootstrap_token is not None else os.getenv("CORE_BOOTSTRAP_TOKEN", "")
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        verify_migrations_current(engine)
        yield
        engine.dispose()

    app = FastAPI(
        title="KOMAROVA_CORE API",
        version="0.2.0",
        description="Private family information core. Development foundation; not yet production-certified.",
        docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan,
    )

    def get_db():
        yield from session_dependency(session_factory)

    def require_current_user(
        authorization: str | None = Header(default=None, alias="Authorization"),
        db: Session = Depends(get_db),
    ) -> User:
        if not configured_jwt_secret:
            raise HTTPException(status_code=503, detail="Authentication is locked: CORE_JWT_SECRET must contain at least 32 characters")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Bearer access token required")
        try:
            claims = decode_access_token(authorization[7:].strip(), configured_jwt_secret)
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid or expired access token")
        user = db.get(User, claims["sub"])
        if user is None or user.status != "active":
            raise HTTPException(status_code=401, detail="Account is unavailable")
        session = db.scalar(select(AuthSession).where(
            AuthSession.token_jti == claims["jti"],
            AuthSession.user_id == user.user_id,
            AuthSession.revoked_at.is_(None),
            AuthSession.expires_at > utc_now(),
        ))
        if session is None:
            raise HTTPException(status_code=401, detail="Session is expired or revoked")
        return user

    def require_roles(*allowed_roles: str):
        def dependency(user: User = Depends(require_current_user)) -> User:
            if user.role not in allowed_roles:
                raise HTTPException(status_code=403, detail="Insufficient role permissions")
            return user
        return dependency

    configured_media_root = Path(
        media_root if media_root is not None else os.getenv("CORE_MEDIA_ROOT", "./private_media")
    )
    cors_origins = [
        origin.strip().rstrip("/")
        for origin in os.getenv(
            "CORE_CORS_ORIGINS",
            "https://alexsandrkomarov1-wq.github.io",
        ).split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Core-Bootstrap-Token"],
        max_age=600,
    )
    app.include_router(build_archive_router(get_db, require_roles, configured_media_root))
    app.include_router(build_google_drive_router(get_db, require_current_user))

    def acquire_security_lock(db: Session) -> None:
        # A single database row serializes bootstrap and owner-administration writes
        # across processes. UPDATE obtains a row/write lock until transaction commit.
        result = db.execute(
            update(SystemState)
            .where(SystemState.state_key == "security_admin")
            .values(version=SystemState.version + 1)
        )
        if result.rowcount != 1:
            raise RuntimeError("Required security_admin lock row is missing; apply migrations")

    def audit(db: Session, event_type: str, entity_type: str, entity_id: str, actor_id: str, details: dict):
        db.add(AuditEvent(
            event_type=event_type, entity_type=entity_type, entity_id=entity_id,
            actor_id=actor_id, details=json.dumps(details, ensure_ascii=False),
        ))

    def create_user_record(db: Session, username: str, password: str, role: str) -> User:
        user = User(username=username, password_hash=hash_password(password), role=role)
        db.add(user)
        db.flush()
        return user

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "komarova-core-api", "version": app.version}

    @app.post("/api/v1/auth/bootstrap", response_model=UserRead, status_code=201)
    def bootstrap_owner(
        payload: BootstrapCreate,
        x_core_bootstrap_token: str | None = Header(default=None, alias="X-Core-Bootstrap-Token"),
        db: Session = Depends(get_db),
    ):
        if not configured_bootstrap_token:
            raise HTTPException(status_code=503, detail="Owner bootstrap is disabled")
        if not x_core_bootstrap_token or not secrets.compare_digest(x_core_bootstrap_token, configured_bootstrap_token):
            raise HTTPException(status_code=401, detail="Valid bootstrap token required")
        try:
            acquire_security_lock(db)
            if db.scalar(select(func.count()).select_from(User)):
                db.rollback()
                raise HTTPException(status_code=409, detail="Bootstrap is available only before the first account")
            owner = create_user_record(db, payload.username, payload.password, "owner")
            audit(db, "user.bootstrap_created", "user", owner.user_id, owner.user_id, {"role": "owner"})
            db.commit()
            db.refresh(owner)
            return owner
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Username is already in use")

    @app.post("/api/v1/auth/login", response_model=TokenRead)
    def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
        if not configured_jwt_secret:
            raise HTTPException(status_code=503, detail="Authentication is not configured")
        # Persisted throttling works across API workers and restarts. The client IP is
        # taken from the direct connection; untrusted forwarding headers are ignored.
        acquire_security_lock(db)
        source_ip = request.client.host if request.client else "unknown"
        attempt_key = hashlib.sha256(f"{payload.username}:{source_ip}".encode("utf-8")).hexdigest()
        attempt = db.get(LoginAttempt, attempt_key)
        now = utc_now()
        if attempt and attempt.locked_until and (attempt.locked_until.replace(tzinfo=timezone.utc) if attempt.locked_until.tzinfo is None else attempt.locked_until) > now:
            db.rollback()
            raise HTTPException(status_code=429, detail="Too many login attempts; try again later")
        if attempt and (now - (attempt.window_started_at.replace(tzinfo=timezone.utc) if attempt.window_started_at.tzinfo is None else attempt.window_started_at)).total_seconds() > 900:
            attempt.failed_attempts = 0
            attempt.window_started_at = now
            attempt.locked_until = None
        user = db.scalar(select(User).where(User.username == payload.username))
        valid = user is not None and verify_password(payload.password, user.password_hash)
        if not valid or user.status != "active":
            if attempt is None:
                attempt = LoginAttempt(attempt_key=attempt_key, failed_attempts=0, window_started_at=now)
                db.add(attempt)
            attempt.failed_attempts += 1
            if attempt.failed_attempts >= 5:
                attempt.locked_until = now + __import__("datetime").timedelta(minutes=15)
            db.commit()
            raise HTTPException(status_code=401, detail="Invalid username or password")
        if attempt is not None:
            db.delete(attempt)
        token, token_jti, expires_at = create_access_token(user.user_id, configured_jwt_secret)
        session = AuthSession(user_id=user.user_id, token_jti=token_jti, expires_at=expires_at)
        db.add(session)
        db.flush()
        audit(db, "auth.session_created", "user", user.user_id, user.user_id, {"session_id": session.session_id})
        db.commit()
        return TokenRead(access_token=token, expires_in=ACCESS_TOKEN_SECONDS, user=user)

    @app.get("/api/v1/auth/me", response_model=UserRead)
    def get_me(user: User = Depends(require_current_user)):
        return user

    @app.post("/api/v1/auth/logout")
    def logout(
        authorization: str | None = Header(default=None, alias="Authorization"),
        user: User = Depends(require_current_user),
        db: Session = Depends(get_db),
    ):
        claims = decode_access_token(authorization[7:].strip(), configured_jwt_secret)
        session = db.scalar(select(AuthSession).where(AuthSession.token_jti == claims["jti"]))
        if session is not None and session.revoked_at is None:
            session.revoked_at = utc_now()
            audit(db, "auth.session_revoked", "user", user.user_id, user.user_id, {"session_id": session.session_id})
            db.commit()
        return {"status": "revoked"}

    @app.post("/api/v1/auth/change-password")
    def change_password(
        payload: PasswordChange,
        authorization: str | None = Header(default=None, alias="Authorization"),
        user: User = Depends(require_current_user),
        db: Session = Depends(get_db),
    ):
        if not verify_password(payload.current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        if payload.current_password == payload.new_password:
            raise HTTPException(status_code=422, detail="New password must differ from the current password")
        user.password_hash = hash_password(payload.new_password)
        now = utc_now()
        sessions = db.scalars(select(AuthSession).where(
            AuthSession.user_id == user.user_id,
            AuthSession.revoked_at.is_(None),
        )).all()
        for active_session in sessions:
            active_session.revoked_at = now
        audit(db, "auth.password_changed", "user", user.user_id, user.user_id, {
            "revoked_sessions": len(sessions),
        })
        db.commit()
        return {"status": "password_changed", "reauthentication_required": True}

    @app.get("/api/v1/auth/sessions", response_model=list[SessionRead])
    def list_sessions(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
        return list(db.scalars(
            select(AuthSession).where(AuthSession.user_id == user.user_id)
            .order_by(AuthSession.created_at.desc())
        ).all())

    @app.post("/api/v1/users", response_model=UserRead, status_code=201)
    def create_user(
        payload: UserCreate,
        actor: User = Depends(require_roles("owner", "moderator")),
        db: Session = Depends(get_db),
    ):
        acquire_security_lock(db)
        db.refresh(actor)
        if actor.status != "active":
            raise HTTPException(status_code=401, detail="Account is unavailable")
        if actor.role not in {"owner", "moderator"}:
            raise HTTPException(status_code=403, detail="Insufficient role permissions")
        if actor.role == "moderator" and payload.role not in {"family_member", "guest"}:
            raise HTTPException(status_code=403, detail="Moderators may create family_member or guest accounts only")
        try:
            user = create_user_record(db, payload.username, payload.password, payload.role)
            audit(db, "user.created", "user", user.user_id, actor.user_id, {"username": user.username, "role": user.role})
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="Username is already in use")

    @app.get("/api/v1/users", response_model=list[UserRead])
    def list_users(
        _: User = Depends(require_roles("owner", "moderator")),
        db: Session = Depends(get_db),
    ):
        return list(db.scalars(select(User).order_by(User.username)).all())

    @app.patch("/api/v1/users/{user_id}", response_model=UserRead)
    def update_user(
        user_id: str,
        payload: UserUpdate,
        actor: User = Depends(require_roles("owner", "moderator")),
        db: Session = Depends(get_db),
    ):
        acquire_security_lock(db)
        db.refresh(actor)
        if actor.status != "active":
            raise HTTPException(status_code=401, detail="Account is unavailable")
        if actor.role not in {"owner", "moderator"}:
            raise HTTPException(status_code=403, detail="Insufficient role permissions")
        target = db.get(User, user_id)
        if target is None:
            raise HTTPException(status_code=404, detail="User not found")
        if actor.role == "moderator":
            if payload.role is not None:
                raise HTTPException(status_code=403, detail="Only the owner may change account roles")
            if target.role not in {"family_member", "guest"}:
                raise HTTPException(status_code=403, detail="Moderators may manage family_member or guest accounts only")
        if payload.role is not None and actor.role != "owner":
            raise HTTPException(status_code=403, detail="Only the owner may change account roles")
        if target.role == "owner" and (payload.role not in (None, "owner") or payload.status == "disabled"):
            active_owners = db.scalar(select(func.count()).select_from(User).where(
                User.role == "owner", User.status == "active"
            )) or 0
            if active_owners <= 1:
                raise HTTPException(status_code=409, detail="The last active owner account cannot be removed or demoted")
        old_role, old_status = target.role, target.status
        if payload.role is not None:
            target.role = payload.role
        if payload.status is not None:
            target.status = payload.status
        revoked_sessions = 0
        if old_status == "active" and target.status == "disabled":
            now = utc_now()
            active_sessions = db.scalars(select(AuthSession).where(
                AuthSession.user_id == target.user_id,
                AuthSession.revoked_at.is_(None),
            )).all()
            for active_session in active_sessions:
                active_session.revoked_at = now
            revoked_sessions = len(active_sessions)
        audit(db, "user.updated", "user", target.user_id, actor.user_id, {
            "old_role": old_role, "new_role": target.role,
            "old_status": old_status, "new_status": target.status,
            "revoked_sessions": revoked_sessions,
        })
        db.commit()
        db.refresh(target)
        return target

    @app.get("/api/v1/navigation")
    def get_navigation(user: User = Depends(require_current_user)):
        """Return the role-aware menu manifest for the private application."""
        return build_navigation(user.role)

    @app.get("/api/v1/search")
    def search_registry(
        q: str = Query(min_length=2, max_length=100),
        limit: int = Query(default=20, ge=1, le=50),
        db: Session = Depends(get_db),
        _: User = Depends(require_current_user),
    ):
        """Search the implemented private registry without exposing it publicly.

        Python casefold is used so Cyrillic names are searchable regardless of
        letter case on SQLite, whose built-in case-insensitive LIKE is ASCII-only.
        """
        needle = " ".join(q.split()).casefold()
        if len(needle) < 2:
            raise HTTPException(status_code=422, detail="Search query must contain at least two non-space characters")

        people = db.scalars(
            select(Person)
            .where(Person.status == "active")
            .order_by(Person.display_name, Person.person_id)
        ).all()
        matches = [
            person for person in people
            if needle in person.display_name.casefold()
            or needle in person.person_id.casefold()
        ]
        return {
            "query": " ".join(q.split()),
            "total": len(matches),
            "items": [
                {
                    "kind": "person",
                    "entity_id": person.person_id,
                    "title": person.display_name,
                    "description": f"PERSON-ID: {person.person_id}",
                    "api_endpoint": f"/api/v1/people/{person.person_id}",
                }
                for person in matches[:limit]
            ],
        }

    @app.post("/api/v1/people", response_model=PersonRead, status_code=201)
    def create_person(
        payload: PersonCreate, db: Session = Depends(get_db),
        actor: User = Depends(require_roles("owner", "moderator", "family_member")),
    ):
        person = Person(display_name=payload.display_name)
        db.add(person)
        db.flush()
        audit(db, "person.created", "person", person.person_id, actor.user_id, {"display_name": person.display_name})
        db.commit()
        db.refresh(person)
        return person

    @app.get("/api/v1/people", response_model=list[PersonRead])
    def list_people(
        include_archived: bool = False,
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        db: Session = Depends(get_db),
        _: User = Depends(require_current_user),
    ):
        query = select(Person)
        if not include_archived:
            query = query.where(Person.status == "active")
        query = query.order_by(Person.created_at, Person.person_id).limit(limit).offset(offset)
        return list(db.scalars(query).all())

    @app.get("/api/v1/people/{person_id}", response_model=PersonRead)
    def get_person(person_id: str, db: Session = Depends(get_db), _: User = Depends(require_current_user)):
        person = db.get(Person, person_id)
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        return person

    @app.patch("/api/v1/people/{person_id}", response_model=PersonRead)
    def update_person(
        person_id: str, payload: PersonUpdate, db: Session = Depends(get_db),
        actor: User = Depends(require_roles("owner", "moderator")),
    ):
        person = db.get(Person, person_id)
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        if person.status == "archived":
            raise HTTPException(status_code=409, detail="Archived person cannot be edited")
        old_name = person.display_name
        person.display_name = payload.display_name
        audit(db, "person.updated", "person", person.person_id, actor.user_id, {
            "old_display_name": old_name, "new_display_name": person.display_name,
        })
        db.commit()
        db.refresh(person)
        return person

    @app.delete("/api/v1/people/{person_id}", response_model=PersonRead)
    def archive_person(
        person_id: str, db: Session = Depends(get_db),
        actor: User = Depends(require_roles("owner", "moderator")),
    ):
        person = db.get(Person, person_id)
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        if person.status != "archived":
            person.status = "archived"
            audit(db, "person.archived", "person", person.person_id, actor.user_id, {})
            db.commit()
            db.refresh(person)
        return person

    @app.post("/api/v1/relationships", response_model=RelationshipRead, status_code=201)
    def create_relationship(
        payload: RelationshipCreate, db: Session = Depends(get_db),
        actor: User = Depends(require_roles("owner", "moderator", "family_member")),
    ):
        if payload.from_person_id == payload.to_person_id:
            raise HTTPException(status_code=422, detail="A person cannot be related to themselves")
        first = db.get(Person, payload.from_person_id)
        second = db.get(Person, payload.to_person_id)
        if first is None or second is None:
            raise HTTPException(status_code=404, detail="Both people must exist")
        if first.status != "active" or second.status != "active":
            raise HTTPException(status_code=409, detail="Archived people cannot receive new relationships")
        record = RelationshipRecord(
            from_person_id=first.person_id, to_person_id=second.person_id,
            relationship_type=payload.relationship_type,
        )
        db.add(record)
        db.flush()
        audit(db, "relationship.created", "relationship", record.relationship_id, actor.user_id, {
            "from_person_id": record.from_person_id, "to_person_id": record.to_person_id,
            "relationship_type": record.relationship_type,
        })
        db.commit()
        db.refresh(record)
        return record

    @app.get("/api/v1/people/{person_id}/relationships", response_model=list[RelationshipRead])
    def list_relationships(
        person_id: str, db: Session = Depends(get_db), _: User = Depends(require_current_user),
    ):
        if db.get(Person, person_id) is None:
            raise HTTPException(status_code=404, detail="Person not found")
        query = select(RelationshipRecord).where(
            (RelationshipRecord.from_person_id == person_id)
            | (RelationshipRecord.to_person_id == person_id)
        ).order_by(RelationshipRecord.created_at)
        return list(db.scalars(query).all())

    return app


app = create_app()
