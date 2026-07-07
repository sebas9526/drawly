from datetime import datetime

from sqlmodel import Field

from app.database.base import TZ_DATETIME, UUIDAuditBase


class User(UUIDAuditBase, table=True):
    """A platform user (organizer). Owns their raffles/participants/tickets."""

    __tablename__ = "users"

    full_name: str = Field(max_length=150)
    email: str = Field(index=True, unique=True, max_length=150)
    password_hash: str = Field(max_length=255)
    avatar_url: str | None = Field(default=None)
    email_verified_at: datetime | None = Field(default=None, sa_type=TZ_DATETIME, nullable=True)
