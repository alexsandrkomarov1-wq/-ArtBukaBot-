from datetime import datetime
from typing import Literal
import re
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Role = Literal["owner", "moderator", "family_member", "guest"]

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

class BootstrapCreate(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=12, max_length=128)
    @field_validator("username")
    @classmethod
    def clean_username(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{2,79}", value):
            raise ValueError("username must use 3-80 lowercase letters, numbers, dots, underscores or hyphens")
        return value

class UserCreate(BootstrapCreate):
    role: Role

class UserUpdate(BaseModel):
    role: Role | None = None
    status: Literal["active", "disabled"] | None = None
    @model_validator(mode="after")
    def require_change(self):
        if self.role is None and self.status is None:
            raise ValueError("At least one of role or status must be supplied")
        return self

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    username: str
    role: Role
    status: Literal["active", "disabled"]
    created_at: datetime
    updated_at: datetime

class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=1, max_length=128)
    @field_validator("username")
    @classmethod
    def clean_username(cls, value: str) -> str:
        return value.strip().lower()

class TokenRead(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    user: UserRead

class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    session_id: str
    created_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
