from __future__ import annotations
from datetime import datetime, timezone
import secrets
from sqlalchemy import DateTime, ForeignKey, String, Text, BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def new_id(prefix: str) -> str:
    return f"{prefix}-{secrets.token_hex(16).upper()}"

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Person(Base):
    __tablename__ = "people"
    person_id: Mapped[str] = mapped_column(String(34), primary_key=True, default=lambda: new_id("P"))
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

class RelationshipRecord(Base):
    __tablename__ = "relationships"
    relationship_id: Mapped[str] = mapped_column(String(34), primary_key=True, default=lambda: new_id("R"))
    from_person_id: Mapped[str] = mapped_column(ForeignKey("people.person_id"), nullable=False, index=True)
    to_person_id: Mapped[str] = mapped_column(ForeignKey("people.person_id"), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(60), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    event_id: Mapped[str] = mapped_column(String(34), primary_key=True, default=lambda: new_id("A"))
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    actor_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[str] = mapped_column(String(34), primary_key=True, default=lambda: new_id("U"))
    username: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(24), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)

class AuthSession(Base):
    __tablename__ = "auth_sessions"
    session_id: Mapped[str] = mapped_column(String(34), primary_key=True, default=lambda: new_id("S"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    token_jti: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class SystemState(Base):
    __tablename__ = "system_state"
    state_key: Mapped[str] = mapped_column(String(80), primary_key=True)
    version: Mapped[int] = mapped_column(nullable=False, default=0)

class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    attempt_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    failed_attempts: Mapped[int] = mapped_column(nullable=False, default=0)
    window_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class StoredBlob(Base):
    __tablename__ = "stored_blobs"
    blob_id: Mapped[str] = mapped_column(String(35), primary_key=True, default=lambda: new_id("BL"))
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    detected_mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(40), nullable=False, default="local-private")
    storage_object_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    storage_state: Mapped[str] = mapped_column(String(24), nullable=False, default="quarantined")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class ArchiveItem(Base):
    __tablename__ = "archive_items"
    archive_item_id: Mapped[str] = mapped_column(String(35), primary_key=True, default=lambda: new_id("AR"))
    item_type: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[str | None] = mapped_column(String(300), nullable=True)
    record_status: Mapped[str] = mapped_column(String(24), nullable=False, default="quarantined")
    original_blob_id: Mapped[str] = mapped_column(ForeignKey("stored_blobs.blob_id"), nullable=False, unique=True)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)

class ArchiveEntityLink(Base):
    __tablename__ = "archive_entity_links"
    __table_args__ = (
        UniqueConstraint("archive_item_id", "target_entity_type", "target_entity_id", "link_role",
                         name="uq_archive_entity_link"),
    )
    link_id: Mapped[str] = mapped_column(String(35), primary_key=True, default=lambda: new_id("LK"))
    archive_item_id: Mapped[str] = mapped_column(ForeignKey("archive_items.archive_item_id"), nullable=False, index=True)
    target_entity_type: Mapped[str] = mapped_column(String(24), nullable=False)
    target_entity_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    link_role: Mapped[str] = mapped_column(String(32), nullable=False)
    confirmation_status: Mapped[str] = mapped_column(String(16), nullable=False, default="confirmed")
    source_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class GoogleOAuthState(Base):
    __tablename__ = "google_oauth_states"
    state_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class GoogleDriveAccount(Base):
    __tablename__ = "google_drive_accounts"
    drive_account_id: Mapped[str] = mapped_column(String(35), primary_key=True, default=lambda: new_id("GD"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    google_user_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    email_address: Mapped[str] = mapped_column(String(320), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    refresh_token_ciphertext: Mapped[str] = mapped_column(Text, nullable=False)
    granted_scopes: Mapped[str] = mapped_column(Text, nullable=False)
    quota_limit_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    quota_usage_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    quota_usage_in_drive_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    quota_usage_in_trash_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    last_quota_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
