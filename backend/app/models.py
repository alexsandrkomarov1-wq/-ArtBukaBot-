from __future__ import annotations

from datetime import datetime, timezone
import secrets

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def new_id(prefix: str) -> str:
    # 48 random bits; IDs are generated once and never derived from a person's name.
    return f"{prefix}-{secrets.token_hex(6).upper()}"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Person(Base):
    __tablename__ = "people"

    person_id: Mapped[str] = mapped_column(String(14), primary_key=True, default=lambda: new_id("P"))
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now)


class RelationshipRecord(Base):
    __tablename__ = "relationships"

    relationship_id: Mapped[str] = mapped_column(String(14), primary_key=True, default=lambda: new_id("R"))
    from_person_id: Mapped[str] = mapped_column(ForeignKey("people.person_id"), nullable=False, index=True)
    to_person_id: Mapped[str] = mapped_column(ForeignKey("people.person_id"), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(60), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[str] = mapped_column(String(14), primary_key=True, default=lambda: new_id("A"))
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    actor_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
