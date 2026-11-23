from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PersonCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)

    @field_validator("display_name")
    @classmethod
    def clean_display_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("display_name must not be blank")
        return cleaned


class PersonUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=200)

    @field_validator("display_name")
    @classmethod
    def clean_display_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("display_name must not be blank")
        return cleaned


class PersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    person_id: str
    display_name: str
    status: Literal["active", "archived"]
    created_at: datetime
    updated_at: datetime


class RelationshipCreate(BaseModel):
    from_person_id: str = Field(min_length=3, max_length=40)
    to_person_id: str = Field(min_length=3, max_length=40)
    relationship_type: str = Field(min_length=1, max_length=60)

    @field_validator("relationship_type")
    @classmethod
    def clean_relationship_type(cls, value: str) -> str:
        cleaned = " ".join(value.split()).lower()
        if not cleaned:
            raise ValueError("relationship_type must not be blank")
        return cleaned


class RelationshipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    relationship_id: str
    from_person_id: str
    to_person_id: str
    relationship_type: str
    created_at: datetime
