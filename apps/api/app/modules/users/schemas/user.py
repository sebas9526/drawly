import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.users.models import User

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalize_email(value: str) -> str:
    value = value.strip().lower()
    if not _EMAIL_RE.match(value):
        raise ValueError("Invalid email format.")
    return value


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=1, max_length=150)
    email: str = Field(max_length=150)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def _email(cls, value: str) -> str:
        return _normalize_email(value)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(max_length=150)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def _email(cls, value: str) -> str:
        return value.strip().lower()


class UserRead(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    avatar_url: str | None
    email_verified_at: datetime | None
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserRead":
        return cls(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            avatar_url=user.avatar_url,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
        )
