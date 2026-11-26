from __future__ import annotations
from datetime import datetime, timezone
import secrets
from sqlalchemy import DateTime, ForeignKey, String, Text, BigInteger, UniqueConstraint, CheckConstraint, Float
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

class ExternalIdentity(Base):
    """Explicit mapping from an external identity provider to a local role-bearing account."""
    __tablename__ = "external_identities"
    __table_args__ = (
        UniqueConstraint("provider", "subject", name="uq_external_identity_provider_subject"),
        UniqueConstraint("provider", "user_id", name="uq_external_identity_provider_user"),
    )
    identity_id: Mapped[str] = mapped_column(String(35), primary_key=True, default=lambda: new_id("XI"))
    provider: Mapped[str] = mapped_column(String(24), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


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


class Material(Base):
    """Stable material identity; derivatives point to the immutable original material."""
    __tablename__ = "materials"
    material_id: Mapped[str] = mapped_column(String(35), primary_key=True, default=lambda: new_id("M"))
    archive_item_id: Mapped[str] = mapped_column(ForeignKey("archive_items.archive_item_id"), nullable=False, unique=True, index=True)
    original_material_id: Mapped[str | None] = mapped_column(ForeignKey("materials.material_id"), nullable=True, index=True)
    material_role: Mapped[str] = mapped_column(String(16), nullable=False, default="original")
    processing_engine: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class EventRecord(Base):
    __tablename__ = "events"
    event_id: Mapped[str] = mapped_column(String(35), primary_key=True, default=lambda: new_id("E"))
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class PlaceRecord(Base):
    __tablename__ = "places"
    __table_args__ = (CheckConstraint("(latitude IS NULL AND longitude IS NULL) OR (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)", name="ck_places_coordinates"),)
    place_id: Mapped[str] = mapped_column(String(35), primary_key=True, default=lambda: new_id("PL"))
    name: Mapped[str] = mapped_column(String(240), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class PlaceVisit(Base):
    __tablename__ = "place_visits"
    visit_id: Mapped[str] = mapped_column(String(35), primary_key=True, default=lambda: new_id("V"))
    place_id: Mapped[str] = mapped_column(ForeignKey("places.place_id"), nullable=False, index=True)
    visited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class EntityLink(Base):
    __tablename__ = "entity_links"
    __table_args__ = (UniqueConstraint(
        "source_type", "source_id", "target_type", "target_id", "relationship_type",
        name="uq_entity_link_identity",
    ),)
    link_id: Mapped[str] = mapped_column(String(35), primary_key=True, default=lambda: new_id("EL"))
    source_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(48), nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
