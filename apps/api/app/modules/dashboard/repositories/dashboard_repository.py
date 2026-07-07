"""Read-only reporting repository for the dashboard.

This is a *read model*: it composes efficient aggregate queries over the
existing tables (raffles, tickets, participants) rather than issuing many
independent COUNT(*) calls. It never mutates and holds no business rules — those
stay in each domain module. Every query is a single grouped/aggregated statement
so the whole overview is a handful of round-trips.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.modules.collaborators.models import Collaborator
from app.modules.participants.models import Participant
from app.modules.raffles.models import Raffle, RaffleStatus
from app.modules.tickets.models import Ticket, TicketStatus


def _to_float(value: Decimal | int | float | None) -> float:
    return float(value) if value is not None else 0.0


class DashboardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def raffle_aggregates(self, owner_id: uuid.UUID) -> dict[RaffleStatus, tuple[int, float]]:
        """Per-status raffle count + potential value (total_tickets * price) in
        one query, scoped to the owner."""
        statement = (
            select(
                Raffle.status,
                func.count(),
                func.coalesce(func.sum(col(Raffle.total_tickets) * col(Raffle.ticket_price)), 0),
            )
            .where(col(Raffle.deleted_at).is_(None), Raffle.owner_id == owner_id)
            .group_by(col(Raffle.status))
        )
        result = await self._session.execute(statement)
        return {RaffleStatus(row[0]): (int(row[1]), _to_float(row[2])) for row in result.all()}

    async def ticket_aggregates(self, owner_id: uuid.UUID) -> dict[TicketStatus, tuple[int, float]]:
        """Per-status ticket count + value (sum of the raffle price) in one
        query (joined to raffles), scoped to the owner."""
        statement = (
            select(Ticket.status, func.count(), func.coalesce(func.sum(Raffle.ticket_price), 0))
            .join(Raffle, col(Raffle.id) == col(Ticket.raffle_id))
            .where(
                col(Ticket.deleted_at).is_(None),
                col(Raffle.deleted_at).is_(None),
                Ticket.owner_id == owner_id,
            )
            .group_by(col(Ticket.status))
        )
        result = await self._session.execute(statement)
        return {TicketStatus(row[0]): (int(row[1]), _to_float(row[2])) for row in result.all()}

    async def count_participants(self, owner_id: uuid.UUID) -> int:
        statement = select(func.count()).select_from(
            select(Participant)
            .where(col(Participant.deleted_at).is_(None), Participant.owner_id == owner_id)
            .subquery()
        )
        result = await self._session.execute(statement)
        return int(result.scalar_one())

    async def count_collaborators(self, owner_id: uuid.UUID) -> int:
        statement = select(func.count()).select_from(
            select(Collaborator)
            .where(col(Collaborator.deleted_at).is_(None), Collaborator.owner_id == owner_id)
            .subquery()
        )
        result = await self._session.execute(statement)
        return int(result.scalar_one())

    async def recent_reservations(
        self, limit: int, owner_id: uuid.UUID
    ) -> list[tuple[int, datetime, str, str | None]]:
        statement = (
            select(Ticket.number, Ticket.reserved_at, Raffle.title, Participant.full_name)
            .join(Raffle, col(Raffle.id) == col(Ticket.raffle_id))
            .join(Participant, col(Participant.id) == col(Ticket.participant_id), isouter=True)
            .where(
                Ticket.status == TicketStatus.RESERVED,
                col(Ticket.deleted_at).is_(None),
                col(Raffle.deleted_at).is_(None),
                Ticket.owner_id == owner_id,
            )
            .order_by(col(Ticket.reserved_at).desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return [(int(r[0]), r[1], r[2], r[3]) for r in result.all()]

    async def recent_raffles(
        self, limit: int, owner_id: uuid.UUID
    ) -> list[tuple[str, RaffleStatus, int, int]]:
        available = (
            select(func.count())
            .select_from(Ticket)
            .where(
                col(Ticket.raffle_id) == col(Raffle.id),
                Ticket.status == TicketStatus.AVAILABLE,
                col(Ticket.deleted_at).is_(None),
            )
            .correlate(Raffle)
            .scalar_subquery()
        )
        statement = (
            select(Raffle.title, Raffle.status, Raffle.total_tickets, available.label("available"))
            .where(col(Raffle.deleted_at).is_(None), Raffle.owner_id == owner_id)
            .order_by(col(Raffle.created_at).desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return [(r[0], RaffleStatus(r[1]), int(r[2]), int(r[3])) for r in result.all()]
