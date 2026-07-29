import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.participants.models import Participant
from app.modules.participants.validators import is_valid_email


class ParticipantBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @field_validator("email", check_fields=False)
    @classmethod
    def _validate_email(cls, value: str | None) -> str | None:
        if value is not None and value != "" and not is_valid_email(value):
            raise ValueError("Invalid email format.")
        return value or None


class ParticipantCreate(ParticipantBase):
    full_name: str = Field(min_length=1, max_length=150)
    phone: str = Field(min_length=1, max_length=30)
    email: str | None = Field(default=None, max_length=150)
    document: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=2000)
    city: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=2000)


class ParticipantUpdate(ParticipantBase):
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    phone: str | None = Field(default=None, min_length=1, max_length=30)
    email: str | None = Field(default=None, max_length=150)
    document: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=2000)
    city: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=2000)


class ParticipantRead(BaseModel):
    id: uuid.UUID
    full_name: str
    phone: str
    email: str | None
    document: str | None
    address: str | None
    city: str | None
    notes: str | None
    ticket_count: int
    ticket_numbers: list[int]
    collaborator_names: list[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(
        cls,
        participant: Participant,
        *,
        ticket_count: int = 0,
        ticket_numbers: list[int] | None = None,
        collaborator_names: list[str] | None = None,
    ) -> "ParticipantRead":
        return cls(
            id=participant.id,
            full_name=participant.full_name,
            phone=participant.phone,
            email=participant.email,
            document=participant.document,
            address=participant.address,
            city=participant.city,
            notes=participant.notes,
            ticket_count=ticket_count,
            ticket_numbers=ticket_numbers or [],
            collaborator_names=collaborator_names or [],
            created_at=participant.created_at,
            updated_at=participant.updated_at,
        )
