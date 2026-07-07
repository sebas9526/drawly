import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Index, Numeric
from sqlmodel import Field

from app.database.base import UUIDAuditBase, status_column_type

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
    draw_date: datetime
    status: RaffleStatus = Field(
        default=RaffleStatus.DRAFT,
        sa_type=status_column_type(RaffleStatus),
        nullable=False,
        index=True,
    )
    public_slug: str = Field(index=True, unique=True, max_length=120)
