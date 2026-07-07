import uuid

from sqlmodel import Field

from app.database.base import UUIDAuditBase


class Participant(UUIDAuditBase, table=True):
    """A person who owns or is responsible for one or more tickets.

    Designed to evolve into a broader ``Customer`` concept later (one customer
    across many raffles): tickets already link via ``participant_id``, so a future
    rename/extension is additive, not a rewrite. No country-specific validation.
    """

    __tablename__ = "participants"

    # Owner (the authenticated user). Nullable for rows created before auth.
    owner_id: uuid.UUID | None = Field(default=None, foreign_key="users.id", index=True)
    full_name: str = Field(max_length=150)
    phone: str = Field(index=True, max_length=30)
    email: str | None = Field(default=None, index=True, max_length=150)
    document: str | None = Field(default=None, index=True, max_length=50)
    address: str | None = Field(default=None)
    city: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None)
