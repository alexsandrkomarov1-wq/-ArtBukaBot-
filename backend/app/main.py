from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, build_engine, build_session_factory, session_dependency
from .models import AuditEvent, Person, RelationshipRecord
from .schemas import PersonCreate, PersonRead, PersonUpdate, RelationshipCreate, RelationshipRead
from .security import require_api_token


def create_app(database_url: str | None = None, api_token: str | None = None) -> FastAPI:
    engine = build_engine(database_url)
    session_factory = build_session_factory(engine)
    configured_token = api_token if api_token is not None else os.getenv("CORE_API_TOKEN", "")

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        Base.metadata.create_all(bind=engine)
        yield
        engine.dispose()

    app = FastAPI(
        title="KOMAROVA_CORE API",
        version="0.1.0",
        description="Private family information core. Development foundation; not yet production-certified.",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.state.api_token = configured_token

    def get_db():
        yield from session_dependency(session_factory)

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "komarova-core-api", "version": app.version}

    @app.post("/api/v1/people", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
    def create_person(
        payload: PersonCreate,
        db: Session = Depends(get_db),
        actor_id: str | None = Depends(require_api_token),
    ):
        person = Person(display_name=payload.display_name)
        db.add(person)
        db.flush()
        db.add(AuditEvent(
            event_type="person.created",
            entity_type="person",
            entity_id=person.person_id,
            actor_id=actor_id,
            details=json.dumps({"display_name": person.display_name}, ensure_ascii=False),
        ))
        db.commit()
        db.refresh(person)
        return person

    @app.get("/api/v1/people", response_model=list[PersonRead])
    def list_people(
        include_archived: bool = False,
        limit: int = Query(default=50, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        db: Session = Depends(get_db),
        _: str | None = Depends(require_api_token),
    ):
        query = select(Person)
        if not include_archived:
            query = query.where(Person.status == "active")
        query = query.order_by(Person.created_at, Person.person_id).limit(limit).offset(offset)
        return list(db.scalars(query).all())

    @app.get("/api/v1/people/{person_id}", response_model=PersonRead)
    def get_person(
        person_id: str,
        db: Session = Depends(get_db),
        _: str | None = Depends(require_api_token),
    ):
        person = db.get(Person, person_id)
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        return person

    @app.patch("/api/v1/people/{person_id}", response_model=PersonRead)
    def update_person(
        person_id: str,
        payload: PersonUpdate,
        db: Session = Depends(get_db),
        actor_id: str | None = Depends(require_api_token),
    ):
        person = db.get(Person, person_id)
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        if person.status == "archived":
            raise HTTPException(status_code=409, detail="Archived person cannot be edited")
        old_name = person.display_name
        person.display_name = payload.display_name
        db.add(AuditEvent(
            event_type="person.updated",
            entity_type="person",
            entity_id=person.person_id,
            actor_id=actor_id,
            details=json.dumps({"old_display_name": old_name, "new_display_name": person.display_name}, ensure_ascii=False),
        ))
        db.commit()
        db.refresh(person)
        return person

    @app.delete("/api/v1/people/{person_id}", response_model=PersonRead)
    def archive_person(
        person_id: str,
        db: Session = Depends(get_db),
        actor_id: str | None = Depends(require_api_token),
    ):
        person = db.get(Person, person_id)
        if person is None:
            raise HTTPException(status_code=404, detail="Person not found")
        if person.status != "archived":
            person.status = "archived"
            db.add(AuditEvent(
                event_type="person.archived",
                entity_type="person",
                entity_id=person.person_id,
                actor_id=actor_id,
                details="{}",
            ))
            db.commit()
            db.refresh(person)
        return person

    @app.post("/api/v1/relationships", response_model=RelationshipRead, status_code=status.HTTP_201_CREATED)
    def create_relationship(
        payload: RelationshipCreate,
        db: Session = Depends(get_db),
        actor_id: str | None = Depends(require_api_token),
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
            from_person_id=first.person_id,
            to_person_id=second.person_id,
            relationship_type=payload.relationship_type,
        )
        db.add(record)
        db.flush()
        db.add(AuditEvent(
            event_type="relationship.created",
            entity_type="relationship",
            entity_id=record.relationship_id,
            actor_id=actor_id,
            details=json.dumps({
                "from_person_id": record.from_person_id,
                "to_person_id": record.to_person_id,
                "relationship_type": record.relationship_type,
            }),
        ))
        db.commit()
        db.refresh(record)
        return record

    @app.get("/api/v1/people/{person_id}/relationships", response_model=list[RelationshipRead])
    def list_relationships(
        person_id: str,
        db: Session = Depends(get_db),
        _: str | None = Depends(require_api_token),
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
