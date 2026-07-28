import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Index, Numeric
from sqlmodel import Field

from app.database.base import TZ_DATETIME, UUIDAuditBase, status_column_type

from .enums import RaffleStatus

# NUMERIC(12, 2) money type; typed Any for SQLModel's sa_type (see base.TZ_DATETIME).
_MONEY: Any = Numeric(12, 2)


class Raffle(UUIDAuditBase, table=True):
    """Raffle aggregate root. Tickets are always managed through a raffle.

    ``organization_id`` is intentionally nullable for now: the organizations
    module does not exist yet, so no FK is declared. It becomes NOT NULL + FK
    when that module lands (see docs/03-database/DATABASE_DESIGN.md).
    """

    __tablename__ = "raffles"
    # Indexed for the dashboard "recent raffles" ordering.
    __table_args__ = (Index("ix_raffles_created_at", "created_at"),)

    # Owner (the authenticated user). Nullable for rows created before auth.
    owner_id: uuid.UUID | None = Field(default=None, foreign_key="users.id", index=True)
    organization_id: uuid.UUID | None = Field(default=None, index=True)
    title: str = Field(max_length=150)
    description: str = Field(default="")
    prize: str = Field(default="")
    cover_image: str | None = Field(default=None)
    ticket_price: Decimal = Field(default=Decimal("0"), sa_type=_MONEY, nullable=False)
    total_tickets: int = Field(ge=1)
    # First ticket number generated (0 or 1 only). Fixed at creation time and
    # never editable afterwards — same immutability rule as total_tickets once
    # tickets exist (see RaffleUpdate, which omits this field entirely).
    starting_number: int = Field(default=1, ge=0, le=1)
    # sa_type required: without it SQLModel maps `datetime` to a naive
    # TIMESTAMP column, which asyncpg then rejects the moment a tz-aware value
    # (every request payload) is bound to it — invisible under the SQLite test
    # suite (no strict tz-awareness check there), only surfaced against real
    # Postgres. See migration 0007_raffle_draw_date_timezone.
    draw_date: datetime = Field(sa_type=TZ_DATETIME)
    # Optional scheduled activation. NULL (default) means "no schedule" —
    # today's behavior of publishing only via an explicit manual action. When
    # set, the in-process sweep (app/modules/raffles/dependencies.
    # sweep_scheduled_raffles) publishes the raffle automatically once this
    # moment passes, subject to the same precondition as a manual publish
    # (tickets must already be generated).
    publish_at: datetime | None = Field(default=None, sa_type=TZ_DATETIME, nullable=True)
    status: RaffleStatus = Field(
        default=RaffleStatus.DRAFT,
        sa_type=status_column_type(RaffleStatus),
        nullable=False,
        index=True,
    )
    # Set only when a *valid* winner (a paid ticket) closes the raffle — the
    # cleanup sweep (app/modules/raffles/dependencies.sweep_closed_raffles)
    # soft-deletes the raffle and its tickets once this is far enough in the
    # past (see settings.raffle_cleanup_grace_hours).
    closed_at: datetime | None = Field(default=None, sa_type=TZ_DATETIME, nullable=True)
    # Reflects the *last* winner-registration attempt, valid or not — not a
    # dedicated "official winner" pointer. If status is CLOSED, the ticket
    # this points to is the confirmed winner (its own status is WINNER). If
    # status is still PUBLISHED and this is set, the last entered ticket
    # number wasn't paid yet: an unresolved attempt, not a hard block — the
    # organizer can retry with another number (see RaffleService.
    # record_winner_attempt / close_with_winner).
    winner_ticket_id: uuid.UUID | None = Field(default=None, foreign_key="tickets.id")
    # Uniqueness is enforced at the application layer only (RaffleRepository.
    # exists_slug + RaffleUseCases._unique_slug), scoped to non-deleted rows —
    # same pattern as participants.phone. A DB-level UNIQUE constraint here
    # would outlive a soft-deleted raffle and permanently block reusing its
    # slug (see migration 0009_raffle_public_slug_not_unique).
    public_slug: str = Field(index=True, max_length=120)
