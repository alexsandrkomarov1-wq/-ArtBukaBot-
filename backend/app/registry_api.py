from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, ConfigDict, model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import EntityLink, EventRecord, Material, Person, PlaceRecord, PlaceVisit, User, utc_now

EntityType = Literal["person", "event", "place", "material"]


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=10000)
    occurred_at: datetime | None = None

    @model_validator(mode="after")
    def clean_title(self):
        self.title = " ".join(self.title.split())
        if not self.title:
            raise ValueError("Event title must not be blank")
        return self


class PlaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=10000)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def validate_coordinates(self):
        self.name = " ".join(self.name.split())
        if not self.name:
            raise ValueError("Place name must not be blank")
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Latitude and longitude must be supplied together")
        return self


class VisitCreate(BaseModel):
    place_id: str = Field(min_length=3, max_length=40)
    visited_at: datetime
    notes: str | None = Field(default=None, max_length=10000)


class LinkCreate(BaseModel):
    source_type: EntityType
    source_id: str = Field(min_length=3, max_length=40)
    target_type: EntityType
    target_id: str = Field(min_length=3, max_length=40)
    relationship_type: str = Field(min_length=1, max_length=48)

    @model_validator(mode="after")
    def validate_link(self):
        self.relationship_type = " ".join(self.relationship_type.split()).lower()
        if not self.relationship_type:
            raise ValueError("Relationship type must not be blank")
        if self.source_type == self.target_type and self.source_id == self.target_id:
            raise ValueError("An entity cannot link to itself")
        return self


def build_registry_router(get_db, require_roles) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["entity-registry"])
    entity_models = {"person": Person, "event": EventRecord, "place": PlaceRecord, "material": Material}
    entity_id_fields = {"person": "person_id", "event": "event_id", "place": "place_id", "material": "material_id"}

    def resolve_entity(db: Session, kind: str, entity_id: str):
        model = entity_models[kind]
        entity = db.get(model, entity_id)
        if entity is None:
            raise HTTPException(status_code=404, detail=f"{kind} entity not found")
        if kind == "person" and entity.status != "active":
            raise HTTPException(status_code=409, detail="Archived people cannot be linked")
        if kind == "event" and entity.status != "active":
            raise HTTPException(status_code=409, detail="Archived events cannot be linked")
        return entity

    @router.post("/events", status_code=201)
    def create_event(payload: EventCreate, db: Session = Depends(get_db),
                     actor: User = Depends(require_roles("owner", "moderator", "family_member"))):
        record = EventRecord(title=payload.title, description=payload.description,
                             occurred_at=payload.occurred_at, created_by_user_id=actor.user_id)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @router.get("/events")
    def list_events(limit: int = Query(default=100, ge=1, le=200), offset: int = Query(default=0, ge=0),
                    db: Session = Depends(get_db), _: User = Depends(require_roles("owner", "moderator", "family_member", "guest"))):
        return list(db.scalars(select(EventRecord).where(EventRecord.status == "active")
                               .order_by(EventRecord.occurred_at, EventRecord.created_at)
                               .limit(limit).offset(offset)).all())

    @router.post("/places", status_code=201)
    def create_place(payload: PlaceCreate, db: Session = Depends(get_db),
                     actor: User = Depends(require_roles("owner", "moderator", "family_member"))):
        record = PlaceRecord(name=payload.name, description=payload.description,
                             latitude=payload.latitude, longitude=payload.longitude,
                             created_by_user_id=actor.user_id)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @router.get("/places")
    def list_places(limit: int = Query(default=100, ge=1, le=200), offset: int = Query(default=0, ge=0),
                    db: Session = Depends(get_db), _: User = Depends(require_roles("owner", "moderator", "family_member", "guest"))):
        return list(db.scalars(select(PlaceRecord).order_by(PlaceRecord.name, PlaceRecord.place_id)
                               .limit(limit).offset(offset)).all())

    @router.post("/places/visits", status_code=201)
    def create_visit(payload: VisitCreate, db: Session = Depends(get_db),
                     actor: User = Depends(require_roles("owner", "moderator", "family_member"))):
        place = db.get(PlaceRecord, payload.place_id)
        if place is None:
            raise HTTPException(status_code=404, detail="PLACE-ID not found")
        record = PlaceVisit(place_id=place.place_id, visited_at=payload.visited_at,
                            notes=payload.notes, created_by_user_id=actor.user_id)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @router.get("/places/{place_id}/visits")
    def list_visits(place_id: str, db: Session = Depends(get_db),
                    _: User = Depends(require_roles("owner", "moderator", "family_member", "guest"))):
        if db.get(PlaceRecord, place_id) is None:
            raise HTTPException(status_code=404, detail="PLACE-ID not found")
        return list(db.scalars(select(PlaceVisit).where(PlaceVisit.place_id == place_id)
                               .order_by(PlaceVisit.visited_at.desc())).all())

    @router.post("/entities/links", status_code=201)
    def create_entity_link(payload: LinkCreate, db: Session = Depends(get_db),
                            actor: User = Depends(require_roles("owner", "moderator", "family_member"))):
        resolve_entity(db, payload.source_type, payload.source_id)
        resolve_entity(db, payload.target_type, payload.target_id)
        record = EntityLink(source_type=payload.source_type, source_id=payload.source_id,
                            target_type=payload.target_type, target_id=payload.target_id,
                            relationship_type=payload.relationship_type, created_by_user_id=actor.user_id)
        db.add(record)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=409, detail="This entity relationship already exists")
        db.refresh(record)
        return record

    @router.get("/entities/links")
    def list_entity_links(entity_type: EntityType, entity_id: str = Query(min_length=3, max_length=40),
                          db: Session = Depends(get_db),
                          _: User = Depends(require_roles("owner", "moderator", "family_member", "guest"))):
        resolve_entity(db, entity_type, entity_id)
        query = select(EntityLink).where(
            ((EntityLink.source_type == entity_type) & (EntityLink.source_id == entity_id))
            | ((EntityLink.target_type == entity_type) & (EntityLink.target_id == entity_id))
        ).order_by(EntityLink.created_at)
        return list(db.scalars(query).all())

    return router
