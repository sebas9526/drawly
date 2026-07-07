import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.tickets.models import Ticket, TicketStatus


class ReserveTicketRequest(BaseModel):
    """Admin reservation body. ``participant_id`` and ``collaborator_id`` are both
    optional — a ticket may be reserved with or without a participant on record
    and with or without a collaborator (seller) credited."""

    model_config = ConfigDict(extra="forbid")

    participant_id: uuid.UUID | None = None
    collaborator_id: uuid.UUID | None = None


class SetCollaboratorRequest(BaseModel):
    """Body for crediting/clearing the collaborator (seller) of a reserved
    ticket. ``collaborator_id = null`` clears it."""

    model_config = ConfigDict(extra="forbid")

    collaborator_id: uuid.UUID | None = None


class AssignParticipantRequest(BaseModel):
    """Body for assigning/changing the participant of a ticket."""

    model_config = ConfigDict(extra="forbid")

    participant_id: uuid.UUID


class TicketRead(BaseModel):
    id: uuid.UUID
    raffle_id: uuid.UUID
    participant_id: uuid.UUID | None
    collaborator_id: uuid.UUID | None
    number: int
    status: TicketStatus
    reserved_at: datetime | None
    expires_at: datetime | None
    sold_at: datetime | None
    winner_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, ticket: Ticket) -> "TicketRead":
        return cls.model_validate(ticket, from_attributes=True)
