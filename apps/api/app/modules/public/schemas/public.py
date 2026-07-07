import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.collaborators.models import Collaborator
from app.modules.participants.schemas import ParticipantCreate
from app.modules.participants.validators import is_valid_email
from app.modules.raffles.models import Raffle
from app.modules.tickets.models import Ticket, TicketStatus


class PublicRaffleView(BaseModel):
    """Public projection of a raffle — no internal id, organization, or status.
    Identified by its public slug only."""

    public_slug: str
    title: str
    description: str
    prize: str
    cover_image: str | None
    ticket_price: float
    draw_date: datetime
    total_tickets: int
    available_count: int
    reserved_count: int
    paid_count: int

    @classmethod
    def from_raffle(cls, raffle: Raffle, counts: dict[TicketStatus, int]) -> "PublicRaffleView":
        return cls(
            public_slug=raffle.public_slug,
            title=raffle.title,
            description=raffle.description,
            prize=raffle.prize,
            cover_image=raffle.cover_image,
            ticket_price=float(raffle.ticket_price),
            draw_date=raffle.draw_date,
            total_tickets=raffle.total_tickets,
            available_count=counts.get(TicketStatus.AVAILABLE, 0),
            reserved_count=counts.get(TicketStatus.RESERVED, 0),
            paid_count=counts.get(TicketStatus.PAID, 0),
        )


class PublicTicketView(BaseModel):
    """Public projection of a ticket — only number and status, never the
    participant or internal id."""

    number: int
    status: TicketStatus

    @classmethod
    def from_ticket(cls, ticket: Ticket) -> "PublicTicketView":
        return cls(number=ticket.number, status=ticket.status)


class PublicCollaboratorView(BaseModel):
    """Public projection of an active collaborator — only what the reserve form
    needs to show a seller picker (no phone, email, notes, or owner)."""

    id: uuid.UUID
    name: str
    color: str

    @classmethod
    def from_collaborator(cls, collaborator: Collaborator) -> "PublicCollaboratorView":
        return cls(id=collaborator.id, name=collaborator.name, color=collaborator.color)


class PublicParticipantInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=1, max_length=150)
    phone: str = Field(min_length=1, max_length=30)
    email: str | None = Field(default=None, max_length=150)
    document: str | None = Field(default=None, max_length=50)

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str | None) -> str | None:
        if value is not None and value != "" and not is_valid_email(value):
            raise ValueError("Invalid email format.")
        return value or None


class PublicReserveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_number: int = Field(ge=1)
    participant: PublicParticipantInput
    # Optional seller credited with the reservation; validated against the raffle.
    collaborator_id: uuid.UUID | None = None

    def to_participant_create(self) -> ParticipantCreate:
        return ParticipantCreate(
            full_name=self.participant.full_name,
            phone=self.participant.phone,
            email=self.participant.email,
            document=self.participant.document,
        )


class PublicReserveResult(BaseModel):
    ticket_number: int
    raffle_title: str
    status: TicketStatus
