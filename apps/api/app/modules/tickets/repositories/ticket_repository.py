import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.database.base import utcnow
from app.modules.raffles.models import Raffle, RaffleStatus
from app.modules.tickets.models import Ticket, TicketStatus


class TicketRepository:
    """Soft-delete-aware persistence for tickets. Only DB access point for the
    module — no query logic in services, use cases, or routers."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_raffle_status(self, raffle_id: uuid.UUID) -> RaffleStatus | None:
        """Reads the parent raffle's status directly, the same way the
        dashboard/analytics modules read across module boundaries for a
        cross-cutting concern — a plain read via the other module's model,
        not a dependency on its use_cases/services/dependencies (which would
        cycle back, since raffles already depends on tickets via
        TicketProvisioning). None if the raffle doesn't exist / is deleted."""
        statement = select(Raffle.status).where(
            Raffle.id == raffle_id, col(Raffle.deleted_at).is_(None)
        )
        result = await self._session.execute(statement)
        status = result.scalars().first()
        return RaffleStatus(status) if status is not None else None

    async def get_raffle_draw_date(self, raffle_id: uuid.UUID) -> datetime | None:
        """The parent raffle's draw_date — used as a reservation's expires_at,
        so an unpaid ticket is only released once the raffle is actually
        about to be drawn, not on a short fixed timer. Same cross-module
        read pattern as get_raffle_status. None if the raffle is missing."""
        statement = select(Raffle.draw_date).where(
            Raffle.id == raffle_id, col(Raffle.deleted_at).is_(None)
        )
        result = await self._session.execute(statement)
        return result.scalars().first()

    async def add_all(self, tickets: Sequence[Ticket]) -> int:
        self._session.add_all(list(tickets))
        await self._session.flush()
        return len(tickets)

    async def count_by_raffle(self, raffle_id: uuid.UUID) -> int:
        statement = select(func.count()).select_from(
            select(Ticket)
            .where(Ticket.raffle_id == raffle_id, col(Ticket.deleted_at).is_(None))
            .subquery()
        )
        result = await self._session.execute(statement)
        return int(result.scalar_one())

    async def count_with_participant_by_raffle(self, raffle_id: uuid.UUID) -> int:
        statement = select(func.count()).select_from(
            select(Ticket)
            .where(
                Ticket.raffle_id == raffle_id,
                col(Ticket.participant_id).is_not(None),
                col(Ticket.deleted_at).is_(None),
            )
            .subquery()
        )
        result = await self._session.execute(statement)
        return int(result.scalar_one())

    async def get(
        self, ticket_id: uuid.UUID, *, owner_id: uuid.UUID | None = None
    ) -> Ticket | None:
        statement = select(Ticket).where(Ticket.id == ticket_id, col(Ticket.deleted_at).is_(None))
        if owner_id is not None:
            statement = statement.where(Ticket.owner_id == owner_id)
        result = await self._session.execute(statement)
        return result.scalars().first()

    async def get_for_update(
        self, ticket_id: uuid.UUID, *, owner_id: uuid.UUID | None = None
    ) -> Ticket | None:
        """Row-locking fetch (SELECT ... FOR UPDATE) used by reservation so two
        concurrent reservers can't both grab the same ticket. On SQLite the lock
        clause is a no-op; on PostgreSQL it serializes the reservation."""
        statement = (
            select(Ticket)
            .where(Ticket.id == ticket_id, col(Ticket.deleted_at).is_(None))
            .with_for_update()
        )
        if owner_id is not None:
            statement = statement.where(Ticket.owner_id == owner_id)
        result = await self._session.execute(statement)
        return result.scalars().first()

    async def get_by_raffle_and_number(self, raffle_id: uuid.UUID, number: int) -> Ticket | None:
        statement = select(Ticket).where(
            Ticket.raffle_id == raffle_id,
            Ticket.number == number,
            col(Ticket.deleted_at).is_(None),
        )
        result = await self._session.execute(statement)
        return result.scalars().first()

    async def list_by_raffle(
        self, raffle_id: uuid.UUID, *, offset: int, limit: int
    ) -> tuple[list[Ticket], int]:
        base = select(Ticket).where(Ticket.raffle_id == raffle_id, col(Ticket.deleted_at).is_(None))
        total = await self._session.execute(select(func.count()).select_from(base.subquery()))
        items = await self._session.execute(
            base.order_by(col(Ticket.number).asc()).offset(offset).limit(limit)
        )
        return list(items.scalars().all()), int(total.scalar_one())

    async def status_counts(self, raffle_id: uuid.UUID) -> dict[TicketStatus, int]:
        statement = (
            select(Ticket.status, func.count())
            .where(Ticket.raffle_id == raffle_id, col(Ticket.deleted_at).is_(None))
            .group_by(col(Ticket.status))
        )
        result = await self._session.execute(statement)
        return {TicketStatus(row[0]): int(row[1]) for row in result.all()}

    async def list_paginated(
        self,
        *,
        raffle_id: uuid.UUID | None,
        status: TicketStatus | None,
        offset: int,
        limit: int,
        owner_id: uuid.UUID | None = None,
    ) -> tuple[list[Ticket], int]:
        base = select(Ticket).where(col(Ticket.deleted_at).is_(None))
        if owner_id is not None:
            base = base.where(Ticket.owner_id == owner_id)
        if raffle_id is not None:
            base = base.where(Ticket.raffle_id == raffle_id)
        if status is not None:
            base = base.where(Ticket.status == status)

        total = await self._session.execute(select(func.count()).select_from(base.subquery()))
        items = await self._session.execute(
            base.order_by(col(Ticket.number).asc()).offset(offset).limit(limit)
        )
        return list(items.scalars().all()), int(total.scalar_one())

    async def list_available(
        self, raffle_id: uuid.UUID, *, owner_id: uuid.UUID | None = None
    ) -> list[Ticket]:
        statement = (
            select(Ticket)
            .where(
                Ticket.raffle_id == raffle_id,
                Ticket.status == TicketStatus.AVAILABLE,
                col(Ticket.deleted_at).is_(None),
            )
            .order_by(col(Ticket.number).asc())
        )
        if owner_id is not None:
            statement = statement.where(Ticket.owner_id == owner_id)
        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def list_expired_reserved(self, *, now: datetime, limit: int = 500) -> list[Ticket]:
        """RESERVED tickets whose TTL has elapsed, system-wide (no owner
        scoping — expiry applies regardless of which owner's raffle a ticket
        belongs to). Row-locked so the sweep can't race an in-flight cancel/pay.
        Bounded by ``limit`` per run so one sweep tick can't block for too long
        if a large backlog ever accumulates (the next tick picks up the rest).
        """
        statement = (
            select(Ticket)
            .where(
                Ticket.status == TicketStatus.RESERVED,
                col(Ticket.expires_at).is_not(None),
                col(Ticket.expires_at) <= now,
                col(Ticket.deleted_at).is_(None),
            )
            .order_by(col(Ticket.expires_at).asc())
            .limit(limit)
            .with_for_update()
        )
        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def save(self, ticket: Ticket) -> Ticket:
        ticket.updated_at = utcnow()
        self._session.add(ticket)
        await self._session.flush()
        await self._session.refresh(ticket)
        return ticket

    async def count_by_participant(self, participant_id: uuid.UUID) -> int:
        statement = select(func.count()).select_from(
            select(Ticket)
            .where(Ticket.participant_id == participant_id, col(Ticket.deleted_at).is_(None))
            .subquery()
        )
        result = await self._session.execute(statement)
        return int(result.scalar_one())

    async def count_by_participants(
        self, participant_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, int]:
        ids = list(participant_ids)
        if not ids:
            return {}
        statement = (
            select(Ticket.participant_id, func.count())
            .where(col(Ticket.participant_id).in_(ids), col(Ticket.deleted_at).is_(None))
            .group_by(col(Ticket.participant_id))
        )
        result = await self._session.execute(statement)
        return {row[0]: int(row[1]) for row in result.all() if row[0] is not None}

    async def numbers_by_participants(
        self, participant_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, list[int]]:
        """Batch lookup — the ticket numbers each participant holds, so the
        admin table can show them without an N+1 (mirrors count_by_participants)."""
        ids = list(participant_ids)
        if not ids:
            return {}
        statement = (
            select(Ticket.participant_id, Ticket.number)
            .where(col(Ticket.participant_id).in_(ids), col(Ticket.deleted_at).is_(None))
            .order_by(col(Ticket.participant_id), col(Ticket.number).asc())
        )
        result = await self._session.execute(statement)
        out: dict[uuid.UUID, list[int]] = {}
        for participant_id, number in result.all():
            if participant_id is None:
                continue
            out.setdefault(participant_id, []).append(int(number))
        return out

    async def collaborator_ids_by_participants(
        self, participant_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, list[uuid.UUID]]:
        """Batch lookup — the distinct collaborators (sellers) credited on
        each participant's tickets, so the admin table can show "who sold
        it" without an N+1 (mirrors numbers_by_participants)."""
        ids = list(participant_ids)
        if not ids:
            return {}
        statement = (
            select(Ticket.participant_id, Ticket.collaborator_id)
            .where(
                col(Ticket.participant_id).in_(ids),
                col(Ticket.collaborator_id).is_not(None),
                col(Ticket.deleted_at).is_(None),
            )
            .distinct()
        )
        result = await self._session.execute(statement)
        out: dict[uuid.UUID, list[uuid.UUID]] = {}
        for participant_id, collaborator_id in result.all():
            if participant_id is None or collaborator_id is None:
                continue
            out.setdefault(participant_id, []).append(collaborator_id)
        return out

    async def counts_by_collaborator(
        self, raffle_id: uuid.UUID
    ) -> dict[uuid.UUID, tuple[int, int]]:
        """Per-collaborator ``(reserved_count, paid_count)`` for a raffle.

        ``reserved`` counts tickets still pending payment (RESERVED); ``paid``
        counts sold tickets (PAID and WINNER, since a winner was a paid ticket).
        Collaborators with no tickets are absent from the result.
        """
        counted = (TicketStatus.RESERVED, TicketStatus.PAID, TicketStatus.WINNER)
        statement = (
            select(Ticket.collaborator_id, Ticket.status, func.count())
            .where(
                Ticket.raffle_id == raffle_id,
                col(Ticket.deleted_at).is_(None),
                col(Ticket.collaborator_id).is_not(None),
                col(Ticket.status).in_(counted),
            )
            .group_by(col(Ticket.collaborator_id), col(Ticket.status))
        )
        result = await self._session.execute(statement)
        out: dict[uuid.UUID, tuple[int, int]] = {}
        for collaborator_id, status, count in result.all():
            if collaborator_id is None:
                continue
            reserved, paid = out.get(collaborator_id, (0, 0))
            if TicketStatus(status) is TicketStatus.RESERVED:
                reserved += int(count)
            else:
                paid += int(count)
            out[collaborator_id] = (reserved, paid)
        return out

    async def hard_delete_by_raffle(self, raffle_id: uuid.UUID) -> int:
        """Permanently removes every ticket of a raffle — including already
        soft-deleted ones. Used only by the admin "Eliminar rifa" action
        (RaffleUseCases.delete), which the organizer explicitly asked to be a
        real delete, not the soft-delete every other module uses."""
        count = await self._session.execute(
            select(func.count()).select_from(
                select(Ticket).where(Ticket.raffle_id == raffle_id).subquery()
            )
        )
        total = int(count.scalar_one())
        if total == 0:
            return 0
        await self._session.execute(delete(Ticket).where(col(Ticket.raffle_id) == raffle_id))
        await self._session.flush()
        return total

    async def list_by_participant(self, participant_id: uuid.UUID) -> list[Ticket]:
        statement = (
            select(Ticket)
            .where(Ticket.participant_id == participant_id, col(Ticket.deleted_at).is_(None))
            .order_by(col(Ticket.number).asc())
        )
        result = await self._session.execute(statement)
        return list(result.scalars().all())
