import uuid
from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from app.database.base import TZ_DATETIME, UUIDAuditBase, status_column_type

from .enums import TicketStatus


class Ticket(UUIDAuditBase, table=True):
    """A numbered ticket inside a raffle.

    Both ``raffle_id`` and ``participant_id`` are real FKs (both modules exist).
    ``participant_id`` is nullable — a ticket may have zero or one participant.
    """

    __tablename__ = "tickets"
    __table_args__ = (UniqueConstraint("raffle_id", "number", name="uq_ticket_raffle_number"),)

    # Owner (denormalized from the raffle) so ticket queries can be owner-scoped
    # without a join. Nullable for rows created before auth.
    owner_id: uuid.UUID | None = Field(default=None, foreign_key="users.id", index=True)
    raffle_id: uuid.UUID = Field(foreign_key="raffles.id", index=True)
    participant_id: uuid.UUID | None = Field(
        default=None, foreign_key="participants.id", index=True
    )
    # Collaborator (seller) credited with the reservation/sale. Nullable: an
    # available ticket has none, and recording the seller is optional.
    collaborator_id: uuid.UUID | None = Field(
        default=None, foreign_key="collaborators.id", index=True
    )
    number: int = Field(index=True, ge=1)
    status: TicketStatus = Field(
        default=TicketStatus.AVAILABLE,
        sa_type=status_column_type(TicketStatus),
        nullable=False,
        index=True,
    )
    # Indexed for the dashboard "recent reservations" ordering.
    reserved_at: datetime | None = Field(
        default=None, sa_type=TZ_DATETIME, nullable=True, index=True
    )
    expires_at: datetime | None = Field(default=None, sa_type=TZ_DATETIME, nullable=True)
    sold_at: datetime | None = Field(default=None, sa_type=TZ_DATETIME, nullable=True)
    winner_at: datetime | None = Field(default=None, sa_type=TZ_DATETIME, nullable=True)
