import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.collaborators.models import Collaborator

# #RGB, #RRGGBB or #RRGGBBAA hex colors.
_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class CollaboratorBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("color", check_fields=False)
    @classmethod
    def _validate_color(cls, value: str | None) -> str | None:
        if value is not None and not _HEX_COLOR_RE.match(value):
            raise ValueError("Color must be a hex value like #4F46E5.")
        return value

    @field_validator("email", check_fields=False)
    @classmethod
    def _validate_email(cls, value: str | None) -> str | None:
        if value is not None and value != "" and not _EMAIL_RE.match(value):
            raise ValueError("Invalid email format.")
        return value or None


class CollaboratorCreate(CollaboratorBase):
    raffle_ids: list[uuid.UUID] = Field(min_length=1)
    name: str = Field(min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=150)
    color: str = Field(default="#4F46E5", max_length=9)
    notes: str | None = Field(default=None, max_length=2000)
    is_active: bool = True


class CollaboratorUpdate(CollaboratorBase):
    # None = leave the raffle links untouched; a list replaces the whole set
    # (never an incremental add/remove) — same semantics as
    # CollaboratorRepository.set_raffles.
    raffle_ids: list[uuid.UUID] | None = Field(default=None, min_length=1)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=150)
    color: str | None = Field(default=None, max_length=9)
    notes: str | None = Field(default=None, max_length=2000)
    is_active: bool | None = None


class SetRaffleCollaboratorsRequest(BaseModel):
    """Replaces the full set of collaborators linked to a raffle — driven
    from the raffle form. Unlike CollaboratorCreate/Update.raffle_ids, an
    empty list is valid (a raffle can end up with zero collaborators)."""

    model_config = ConfigDict(extra="forbid")

    collaborator_ids: list[uuid.UUID]


class CollaboratorRead(BaseModel):
    id: uuid.UUID
    raffle_ids: list[uuid.UUID]
    name: str
    phone: str | None
    email: str | None
    color: str
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(
        cls, collaborator: Collaborator, raffle_ids: list[uuid.UUID]
    ) -> "CollaboratorRead":
        return cls(
            id=collaborator.id,
            raffle_ids=raffle_ids,
            name=collaborator.name,
            phone=collaborator.phone,
            email=collaborator.email,
            color=collaborator.color,
            notes=collaborator.notes,
            is_active=collaborator.is_active,
            created_at=collaborator.created_at,
            updated_at=collaborator.updated_at,
        )


class CollaboratorStats(BaseModel):
    """Per-collaborator sales figures within a raffle (no payments yet — derived
    purely from ticket statuses). ``reserved`` = still pending payment,
    ``paid`` = sold, ``total`` = reserved + paid, ``total_value`` = total * price."""

    collaborator_id: uuid.UUID
    name: str
    color: str
    reserved: int
    paid: int
    total: int
    total_value: float
