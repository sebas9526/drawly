import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.raffles.models import Raffle, RaffleStatus


class RaffleCreate(BaseModel):
    """Request body for POST /raffles. Backend re-validates every field (never
    trusts the client); mirrors packages/api-client CreateRaffleRequest."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=150)
    description: str = Field(default="", max_length=5000)
    prize: str = Field(default="", max_length=2000)
    ticket_price: Decimal = Field(default=Decimal("0"), ge=0)
    total_tickets: int = Field(ge=1, le=100_000)
    # First ticket number to generate: "1" -> 1..total, "0" -> 0..total-1.
    # Restricted to 0/1 (not arbitrary) and immutable once set — see
    # RaffleUpdate, which deliberately has no starting_number field.
    starting_number: Literal[0, 1] = 1
    draw_date: datetime
    # Optional scheduled activation. When set, the raffle publishes itself
    # automatically once this moment passes (still requires tickets to
    # already be generated — same precondition as a manual publish). Leave
    # unset to keep today's fully-manual "click Publicar" behavior.
    publish_at: datetime | None = None


class RaffleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    prize: str | None = Field(default=None, max_length=2000)
    ticket_price: Decimal | None = Field(default=None, ge=0)
    total_tickets: int | None = Field(default=None, ge=1, le=100_000)
    draw_date: datetime | None = None
    publish_at: datetime | None = None


class RaffleRead(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None
    title: str
    description: str
    prize: str
    cover_image: str | None
    ticket_price: float
    total_tickets: int
    starting_number: int
    draw_date: datetime
    publish_at: datetime | None
    status: RaffleStatus
    public_slug: str
    closed_at: datetime | None
    winner_ticket_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, raffle: Raffle) -> "RaffleRead":
        return cls(
            id=raffle.id,
            organization_id=raffle.organization_id,
            title=raffle.title,
            description=raffle.description,
            prize=raffle.prize,
            cover_image=raffle.cover_image,
            ticket_price=float(raffle.ticket_price),
            total_tickets=raffle.total_tickets,
            starting_number=raffle.starting_number,
            draw_date=raffle.draw_date,
            publish_at=raffle.publish_at,
            status=raffle.status,
            public_slug=raffle.public_slug,
            closed_at=raffle.closed_at,
            winner_ticket_id=raffle.winner_ticket_id,
            created_at=raffle.created_at,
            updated_at=raffle.updated_at,
        )


class GenerateTicketsResult(BaseModel):
    """Response for the explicit ticket-generation action."""

    raffle_id: uuid.UUID
    generated: int


class RegisterWinnerRequest(BaseModel):
    """Request body for PATCH /raffles/{id}/winner — manual winner entry."""

    model_config = ConfigDict(extra="forbid")

    # ge=0: a raffle may start numbering at 0 (RaffleCreate.starting_number).
    ticket_number: int = Field(ge=0)


class RegisterWinnerResult(BaseModel):
    """Response for PATCH /raffles/{id}/winner. ``valid=False`` means the
    entered number wasn't paid — nothing closed, no winner confirmed, and the
    organizer can just try another number."""

    valid: bool
    ticket_number: int
    participant_id: uuid.UUID | None
    winner_at: datetime | None
