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
    # Needed so the public portal can zero-pad ticket numbers correctly when a
    # raffle starts numbering at 0 (e.g. "00".."99" instead of "01".."100").
    starting_number: int
    available_count: int
    reserved_count: int
    paid_count: int
    # Populated only once the raffle is CLOSED with a confirmed (paid) winner
    # — never for an unresolved "sin ganador válido" attempt, and never
    # phone/document, just enough for a public announcement.
    winner_ticket_number: int | None = None
    winner_participant_name: str | None = None

    @classmethod
    def from_raffle(
        cls,
        raffle: Raffle,
        counts: dict[TicketStatus, int],
        *,
        winner_ticket_number: int | None = None,
        winner_participant_name: str | None = None,
    ) -> "PublicRaffleView":
        return cls(
            public_slug=raffle.public_slug,
            title=raffle.title,
            description=raffle.description,
            prize=raffle.prize,
            cover_image=raffle.cover_image,
            ticket_price=float(raffle.ticket_price),
            draw_date=raffle.draw_date,
            total_tickets=raffle.total_tickets,
            starting_number=raffle.starting_number,
            available_count=counts.get(TicketStatus.AVAILABLE, 0),
            reserved_count=counts.get(TicketStatus.RESERVED, 0),
            paid_count=counts.get(TicketStatus.PAID, 0),
            winner_ticket_number=winner_ticket_number,
            winner_participant_name=winner_participant_name,
        )


class PublicReferralRaffleView(BaseModel):
    """One of a collaborator's published raffles, shown on their personal
    referral link (/ref/{collaborator_id}) when they sell for more than one —
    just enough to pick which one, no internal ids."""

    public_slug: str
    title: str
    prize: str
    cover_image: str | None

    @classmethod
    def from_raffle(cls, raffle: Raffle) -> "PublicReferralRaffleView":
        return cls(
            public_slug=raffle.public_slug,
            title=raffle.title,
            prize=raffle.prize,
            cover_image=raffle.cover_image,
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

    # ge=0: a raffle may start numbering at 0 (RaffleCreate.starting_number).
    ticket_number: int = Field(ge=0)
    participant: PublicParticipantInput
    # Required (public flow only — the admin endpoint keeps it optional):
    # every public reservation must be attributable to a seller, since that's
    # who the organizer collects payment from. Still validated against the
    # raffle in TicketUseCases._validate_collaborator.
    collaborator_id: uuid.UUID

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
