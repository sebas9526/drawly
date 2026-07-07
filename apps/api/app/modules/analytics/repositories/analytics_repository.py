"""Read-only aggregation queries for the analytics module.

Every method is a single grouped/aggregated SQL statement (no per-row Python
loops issuing further queries), always scoped to ``owner_id`` and always
excluding soft-deleted rows. This module owns its own queries rather than
importing ``app.modules.dashboard`` so the two read models can evolve
independently (Sprint 9 requirement).

Filter semantics (``AnalyticsFilters``, see ``schemas/filters.py``):
- ``start_date`` / ``end_date`` bound ``Ticket.reserved_at`` (every reserved,
  paid or winner ticket has it set) for every method except ``sales_by_day``,
  which buckets by ``Ticket.sold_at`` since it reports sales *by day sold*.
- ``raffle_id`` / ``collaborator_id`` scope the counted tickets to one raffle
  and/or one collaborator.
- ``status`` (a ``TicketStatus``) restricts which tickets are counted; it is
  not applied to ``raffles_report_rows`` (a raffle's own lifecycle status is a
  separate concept — see the router's ``raffle_status`` param) nor to the
  collaborator/participant reports, which already break results out by ticket
  status (reserved vs paid) as their core content.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlmodel import col, select

from app.modules.analytics.schemas import AnalyticsFilters
from app.modules.collaborators.models import Collaborator
from app.modules.participants.models import Participant
from app.modules.raffles.models import Raffle, RaffleStatus
from app.modules.tickets.models import Ticket, TicketStatus

_COUNTED_TICKET_STATUSES = (TicketStatus.RESERVED, TicketStatus.PAID, TicketStatus.WINNER)


def _to_float(value: Decimal | int | float | None) -> float:
    return float(value) if value is not None else 0.0


class AnalyticsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _apply_ticket_filters(
        self,
        statement: Any,
        filters: AnalyticsFilters,
        *,
        date_column: Any,
        default_status: TicketStatus | None = None,
    ) -> Any:
        effective_status = filters.status or default_status
        stmt = statement
        if filters.raffle_id is not None:
            stmt = stmt.where(Ticket.raffle_id == filters.raffle_id)
        if effective_status is not None:
            stmt = stmt.where(Ticket.status == effective_status)
        if filters.collaborator_id is not None:
            stmt = stmt.where(Ticket.collaborator_id == filters.collaborator_id)
        if filters.start_date is not None:
            stmt = stmt.where(func.date(col(date_column)) >= filters.start_date)
        if filters.end_date is not None:
            stmt = stmt.where(func.date(col(date_column)) <= filters.end_date)
        return stmt

    # ------------------------------------------------------------------
    # Executive dashboard
    # ------------------------------------------------------------------

    async def raffle_aggregates(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters
    ) -> dict[RaffleStatus, tuple[int, float]]:
        """Per-status raffle count + potential value (total_tickets * price) —
        "expected_revenue" sums the value across every matched raffle."""
        statement = select(
            Raffle.status,
            func.count(),
            func.coalesce(func.sum(col(Raffle.total_tickets) * col(Raffle.ticket_price)), 0),
        ).where(col(Raffle.deleted_at).is_(None), Raffle.owner_id == owner_id)
        if filters.raffle_id is not None:
            statement = statement.where(Raffle.id == filters.raffle_id)
        statement = statement.group_by(col(Raffle.status))
        result = await self._session.execute(statement)
        return {RaffleStatus(row[0]): (int(row[1]), _to_float(row[2])) for row in result.all()}

    async def ticket_aggregates(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters
    ) -> dict[TicketStatus, tuple[int, float]]:
        """Per-status ticket count + value (sum of raffle price), owner-scoped."""
        statement = (
            select(Ticket.status, func.count(), func.coalesce(func.sum(Raffle.ticket_price), 0))
            .join(Raffle, col(Raffle.id) == col(Ticket.raffle_id))
            .where(
                col(Ticket.deleted_at).is_(None),
                col(Raffle.deleted_at).is_(None),
                Ticket.owner_id == owner_id,
            )
        )
        statement = self._apply_ticket_filters(statement, filters, date_column=Ticket.reserved_at)
        statement = statement.group_by(col(Ticket.status))
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

    async def raffle_total_tickets(
        self, owner_id: uuid.UUID, raffle_ids: set[uuid.UUID]
    ) -> dict[uuid.UUID, int]:
        """``total_tickets`` for a set of raffles — used to derive a
        collaborator's participation percentage in the collaborators report."""
        if not raffle_ids:
            return {}
        statement = select(Raffle.id, Raffle.total_tickets).where(
            col(Raffle.id).in_(raffle_ids), Raffle.owner_id == owner_id
        )
        result = await self._session.execute(statement)
        return {r[0]: int(r[1]) for r in result.all()}

    # ------------------------------------------------------------------
    # Raffle report
    # ------------------------------------------------------------------

    def _reserved_or_paid_subquery(self, status: TicketStatus, filters: AnalyticsFilters) -> Any:
        conditions: list[Any] = [
            col(Ticket.raffle_id) == col(Raffle.id),
            Ticket.status == status,
            col(Ticket.deleted_at).is_(None),
        ]
        if filters.collaborator_id is not None:
            conditions.append(Ticket.collaborator_id == filters.collaborator_id)
        if filters.start_date is not None:
            conditions.append(func.date(col(Ticket.reserved_at)) >= filters.start_date)
        if filters.end_date is not None:
            conditions.append(func.date(col(Ticket.reserved_at)) <= filters.end_date)
        return (
            select(func.count())
            .select_from(Ticket)
            .where(*conditions)
            .correlate(Raffle)
            .scalar_subquery()
        )

    async def raffles_report_rows(
        self,
        owner_id: uuid.UUID,
        filters: AnalyticsFilters,
        *,
        raffle_status: RaffleStatus | None,
        offset: int,
        limit: int,
    ) -> tuple[
        list[tuple[uuid.UUID, str, RaffleStatus, datetime, datetime, int, float, int, int]], int
    ]:
        """Rows: (id, title, status, created_at, draw_date, total_tickets,
        ticket_price, reserved, paid). ``expected_revenue`` and ``available``
        are derived by the service from ``total_tickets``/``ticket_price``."""
        reserved_sq = self._reserved_or_paid_subquery(TicketStatus.RESERVED, filters)
        paid_sq = self._reserved_or_paid_subquery(TicketStatus.PAID, filters)

        base = select(Raffle.id).where(
            col(Raffle.deleted_at).is_(None), Raffle.owner_id == owner_id
        )
        if filters.raffle_id is not None:
            base = base.where(Raffle.id == filters.raffle_id)
        if raffle_status is not None:
            base = base.where(Raffle.status == raffle_status)

        total = await self._session.execute(select(func.count()).select_from(base.subquery()))

        # SQLAlchemy/SQLModel's `select()` stub overloads only cover mixed
        # scalar+expression selects up to a handful of columns (confirmed by
        # `dashboard_repository.py`'s narrower selects typechecking cleanly) —
        # this one legitimately needs more, hence the targeted ignore.
        statement = select(  # type: ignore[call-overload]
            Raffle.id,
            Raffle.title,
            Raffle.status,
            Raffle.created_at,
            Raffle.draw_date,
            Raffle.total_tickets,
            Raffle.ticket_price,
            reserved_sq.label("reserved"),
            paid_sq.label("paid"),
        ).where(col(Raffle.deleted_at).is_(None), Raffle.owner_id == owner_id)
        if filters.raffle_id is not None:
            statement = statement.where(Raffle.id == filters.raffle_id)
        if raffle_status is not None:
            statement = statement.where(Raffle.status == raffle_status)
        statement = statement.order_by(col(Raffle.created_at).desc()).offset(offset).limit(limit)

        result = await self._session.execute(statement)
        rows = [
            (
                r[0],
                r[1],
                RaffleStatus(r[2]),
                r[3],
                r[4],
                int(r[5]),
                _to_float(r[6]),
                int(r[7]),
                int(r[8]),
            )
            for r in result.all()
        ]
        return rows, int(total.scalar_one())

    async def raffle_top_collaborators(
        self, raffle_id: uuid.UUID, owner_id: uuid.UUID, limit: int = 5
    ) -> list[tuple[uuid.UUID, str, int, float]]:
        statement = (
            select(
                Collaborator.id,
                Collaborator.name,
                func.count(),
                func.coalesce(func.sum(Raffle.ticket_price), 0),
            )
            .select_from(Ticket)
            .join(Collaborator, col(Collaborator.id) == col(Ticket.collaborator_id))
            .join(Raffle, col(Raffle.id) == col(Ticket.raffle_id))
            .where(
                Ticket.raffle_id == raffle_id,
                Ticket.status == TicketStatus.PAID,
                col(Ticket.deleted_at).is_(None),
                col(Collaborator.deleted_at).is_(None),
                Ticket.owner_id == owner_id,
            )
            .group_by(col(Collaborator.id), col(Collaborator.name))
            .order_by(func.count().desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return [(r[0], r[1], int(r[2]), _to_float(r[3])) for r in result.all()]

    async def raffle_top_participants(
        self, raffle_id: uuid.UUID, owner_id: uuid.UUID, limit: int = 5
    ) -> list[tuple[uuid.UUID, str, int, float]]:
        statement = (
            select(
                Participant.id,
                Participant.full_name,
                func.count(),
                func.coalesce(func.sum(Raffle.ticket_price), 0),
            )
            .select_from(Ticket)
            .join(Participant, col(Participant.id) == col(Ticket.participant_id))
            .join(Raffle, col(Raffle.id) == col(Ticket.raffle_id))
            .where(
                Ticket.raffle_id == raffle_id,
                Ticket.status == TicketStatus.PAID,
                col(Ticket.deleted_at).is_(None),
                col(Participant.deleted_at).is_(None),
                Ticket.owner_id == owner_id,
            )
            .group_by(col(Participant.id), col(Participant.full_name))
            .order_by(func.count().desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return [(r[0], r[1], int(r[2]), _to_float(r[3])) for r in result.all()]

    # ------------------------------------------------------------------
    # Collaborator report
    # ------------------------------------------------------------------

    async def collaborators_report_rows(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters
    ) -> list[tuple[uuid.UUID, str, uuid.UUID, str, TicketStatus | None, int, float]]:
        """One row per (collaborator, ticket_status) — assembled into
        ``CollaboratorReportRow`` (reserved vs paid breakdown) by the service,
        the same per-status grouping idiom as
        ``TicketRepository.counts_by_collaborator``."""
        statement = (
            select(  # type: ignore[call-overload]  # see raffles_report_rows
                Collaborator.id,
                Collaborator.name,
                Collaborator.raffle_id,
                Raffle.title,
                Ticket.status,
                func.count(col(Ticket.id)),
                func.coalesce(func.sum(Raffle.ticket_price), 0),
            )
            .select_from(Collaborator)
            .join(Raffle, col(Raffle.id) == col(Collaborator.raffle_id))
            .join(
                Ticket,
                and_(
                    col(Ticket.collaborator_id) == col(Collaborator.id),
                    col(Ticket.deleted_at).is_(None),
                    col(Ticket.status).in_(_COUNTED_TICKET_STATUSES),
                ),
                isouter=True,
            )
            .where(
                col(Collaborator.deleted_at).is_(None),
                col(Raffle.deleted_at).is_(None),
                Collaborator.owner_id == owner_id,
            )
        )
        if filters.raffle_id is not None:
            statement = statement.where(Collaborator.raffle_id == filters.raffle_id)
        if filters.collaborator_id is not None:
            statement = statement.where(Collaborator.id == filters.collaborator_id)
        if filters.start_date is not None:
            statement = statement.where(
                or_(
                    col(Ticket.id).is_(None),
                    func.date(col(Ticket.reserved_at)) >= filters.start_date,
                )
            )
        if filters.end_date is not None:
            statement = statement.where(
                or_(
                    col(Ticket.id).is_(None), func.date(col(Ticket.reserved_at)) <= filters.end_date
                )
            )
        statement = statement.group_by(
            col(Collaborator.id),
            col(Collaborator.name),
            col(Collaborator.raffle_id),
            col(Raffle.title),
            col(Ticket.status),
        )
        result = await self._session.execute(statement)
        return [
            (
                r[0],
                r[1],
                r[2],
                r[3],
                TicketStatus(r[4]) if r[4] is not None else None,
                int(r[5]),
                _to_float(r[6]),
            )
            for r in result.all()
        ]

    async def participants_served_by_collaborator(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters
    ) -> dict[uuid.UUID, int]:
        statement = (
            select(Ticket.collaborator_id, func.count(func.distinct(Ticket.participant_id)))
            .join(Raffle, col(Raffle.id) == col(Ticket.raffle_id))
            .where(
                col(Ticket.deleted_at).is_(None),
                col(Raffle.deleted_at).is_(None),
                Ticket.owner_id == owner_id,
                col(Ticket.collaborator_id).is_not(None),
                col(Ticket.participant_id).is_not(None),
                col(Ticket.status).in_(_COUNTED_TICKET_STATUSES),
            )
        )
        if filters.raffle_id is not None:
            statement = statement.where(Ticket.raffle_id == filters.raffle_id)
        if filters.collaborator_id is not None:
            statement = statement.where(Ticket.collaborator_id == filters.collaborator_id)
        if filters.start_date is not None:
            statement = statement.where(func.date(col(Ticket.reserved_at)) >= filters.start_date)
        if filters.end_date is not None:
            statement = statement.where(func.date(col(Ticket.reserved_at)) <= filters.end_date)
        statement = statement.group_by(col(Ticket.collaborator_id))
        result = await self._session.execute(statement)
        return {r[0]: int(r[1]) for r in result.all()}

    # ------------------------------------------------------------------
    # Participant report
    # ------------------------------------------------------------------

    async def participants_report_rows(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters
    ) -> list[tuple[uuid.UUID, str, TicketStatus | None, int, float, datetime | None]]:
        """One row per (participant, ticket_status) — assembled into
        ``ParticipantReportRow`` by the service."""
        statement: Any = (
            select(  # type: ignore[call-overload]  # see raffles_report_rows
                Participant.id,
                Participant.full_name,
                Ticket.status,
                func.count(col(Ticket.id)),
                func.coalesce(func.sum(Raffle.ticket_price), 0),
                func.max(Ticket.sold_at),
            )
            .select_from(Participant)
            .join(
                Ticket,
                and_(
                    col(Ticket.participant_id) == col(Participant.id),
                    col(Ticket.deleted_at).is_(None),
                ),
                isouter=True,
            )
            .join(Raffle, col(Raffle.id) == col(Ticket.raffle_id), isouter=True)
            .where(col(Participant.deleted_at).is_(None), Participant.owner_id == owner_id)
        )
        if (raffle_id := filters.raffle_id) is not None:
            statement = statement.where(
                or_(col(Ticket.id).is_(None), col(Ticket.raffle_id) == raffle_id)
            )
        if (collaborator_id := filters.collaborator_id) is not None:
            statement = statement.where(
                or_(col(Ticket.id).is_(None), col(Ticket.collaborator_id) == collaborator_id)
            )
        if filters.start_date is not None:
            statement = statement.where(
                or_(
                    col(Ticket.id).is_(None),
                    func.date(col(Ticket.reserved_at)) >= filters.start_date,
                )
            )
        if filters.end_date is not None:
            statement = statement.where(
                or_(
                    col(Ticket.id).is_(None), func.date(col(Ticket.reserved_at)) <= filters.end_date
                )
            )
        statement = statement.group_by(
            col(Participant.id), col(Participant.full_name), col(Ticket.status)
        )
        result = await self._session.execute(statement)
        return [
            (
                r[0],
                r[1],
                TicketStatus(r[2]) if r[2] is not None else None,
                int(r[3]),
                _to_float(r[4]),
                r[5],
            )
            for r in result.all()
        ]

    async def raffles_count_by_participant(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters
    ) -> dict[uuid.UUID, int]:
        statement = select(
            Ticket.participant_id, func.count(func.distinct(Ticket.raffle_id))
        ).where(
            col(Ticket.deleted_at).is_(None),
            Ticket.owner_id == owner_id,
            col(Ticket.participant_id).is_not(None),
        )
        if filters.raffle_id is not None:
            statement = statement.where(Ticket.raffle_id == filters.raffle_id)
        if filters.collaborator_id is not None:
            statement = statement.where(Ticket.collaborator_id == filters.collaborator_id)
        if filters.start_date is not None:
            statement = statement.where(func.date(col(Ticket.reserved_at)) >= filters.start_date)
        if filters.end_date is not None:
            statement = statement.where(func.date(col(Ticket.reserved_at)) <= filters.end_date)
        statement = statement.group_by(col(Ticket.participant_id))
        result = await self._session.execute(statement)
        return {r[0]: int(r[1]) for r in result.all()}

    # ------------------------------------------------------------------
    # Global reports (top rankings + time series + distribution)
    # ------------------------------------------------------------------

    async def top_collaborators_global(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters, limit: int
    ) -> list[tuple[uuid.UUID, str, int, float]]:
        statement = (
            select(
                Collaborator.id,
                Collaborator.name,
                func.count(),
                func.coalesce(func.sum(Raffle.ticket_price), 0),
            )
            .select_from(Ticket)
            .join(Collaborator, col(Collaborator.id) == col(Ticket.collaborator_id))
            .join(Raffle, col(Raffle.id) == col(Ticket.raffle_id))
            .where(
                col(Ticket.deleted_at).is_(None),
                col(Collaborator.deleted_at).is_(None),
                col(Raffle.deleted_at).is_(None),
                Ticket.owner_id == owner_id,
                Ticket.status == TicketStatus.PAID,
            )
        )
        statement = self._apply_ranking_filters(statement, filters)
        statement = (
            statement.group_by(col(Collaborator.id), col(Collaborator.name))
            .order_by(func.coalesce(func.sum(Raffle.ticket_price), 0).desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return [(r[0], r[1], int(r[2]), _to_float(r[3])) for r in result.all()]

    async def top_raffles_global(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters, limit: int
    ) -> list[tuple[uuid.UUID, str, int, float]]:
        statement = (
            select(
                Raffle.id,
                Raffle.title,
                func.count(),
                func.coalesce(func.sum(Raffle.ticket_price), 0),
            )
            .select_from(Ticket)
            .join(Raffle, col(Raffle.id) == col(Ticket.raffle_id))
            .where(
                col(Ticket.deleted_at).is_(None),
                col(Raffle.deleted_at).is_(None),
                Ticket.owner_id == owner_id,
                Ticket.status == TicketStatus.PAID,
            )
        )
        statement = self._apply_ranking_filters(statement, filters)
        statement = (
            statement.group_by(col(Raffle.id), col(Raffle.title))
            .order_by(func.coalesce(func.sum(Raffle.ticket_price), 0).desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return [(r[0], r[1], int(r[2]), _to_float(r[3])) for r in result.all()]

    async def top_participants_global(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters, limit: int
    ) -> list[tuple[uuid.UUID, str, int, float]]:
        statement = (
            select(
                Participant.id,
                Participant.full_name,
                func.count(),
                func.coalesce(func.sum(Raffle.ticket_price), 0),
            )
            .select_from(Ticket)
            .join(Participant, col(Participant.id) == col(Ticket.participant_id))
            .join(Raffle, col(Raffle.id) == col(Ticket.raffle_id))
            .where(
                col(Ticket.deleted_at).is_(None),
                col(Participant.deleted_at).is_(None),
                col(Raffle.deleted_at).is_(None),
                Ticket.owner_id == owner_id,
                Ticket.status == TicketStatus.PAID,
            )
        )
        statement = self._apply_ranking_filters(statement, filters)
        statement = (
            statement.group_by(col(Participant.id), col(Participant.full_name))
            .order_by(func.coalesce(func.sum(Raffle.ticket_price), 0).desc())
            .limit(limit)
        )
        result = await self._session.execute(statement)
        return [(r[0], r[1], int(r[2]), _to_float(r[3])) for r in result.all()]

    def _apply_ranking_filters(self, statement: Any, filters: AnalyticsFilters) -> Any:
        """Shared filter set for the three "top-N" rankings above (status is
        fixed to PAID by each caller, so it is intentionally not reapplied)."""
        stmt = statement
        if filters.raffle_id is not None:
            stmt = stmt.where(Ticket.raffle_id == filters.raffle_id)
        if filters.collaborator_id is not None:
            stmt = stmt.where(Ticket.collaborator_id == filters.collaborator_id)
        if filters.start_date is not None:
            stmt = stmt.where(func.date(col(Ticket.reserved_at)) >= filters.start_date)
        if filters.end_date is not None:
            stmt = stmt.where(func.date(col(Ticket.reserved_at)) <= filters.end_date)
        return stmt

    async def sales_by_day(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters
    ) -> list[tuple[date, int, float]]:
        """Ticket count + value marked PAID on each day (bucketed by
        ``sold_at``, not ``reserved_at`` — this reports sales, not reservations)."""
        statement = (
            select(
                func.date(col(Ticket.sold_at)).label("day"),
                func.count(),
                func.coalesce(func.sum(Raffle.ticket_price), 0),
            )
            .join(Raffle, col(Raffle.id) == col(Ticket.raffle_id))
            .where(
                col(Ticket.deleted_at).is_(None),
                col(Raffle.deleted_at).is_(None),
                Ticket.owner_id == owner_id,
                Ticket.status == TicketStatus.PAID,
                col(Ticket.sold_at).is_not(None),
            )
        )
        if filters.raffle_id is not None:
            statement = statement.where(Ticket.raffle_id == filters.raffle_id)
        if filters.collaborator_id is not None:
            statement = statement.where(Ticket.collaborator_id == filters.collaborator_id)
        if filters.start_date is not None:
            statement = statement.where(func.date(col(Ticket.sold_at)) >= filters.start_date)
        if filters.end_date is not None:
            statement = statement.where(func.date(col(Ticket.sold_at)) <= filters.end_date)
        statement = statement.group_by("day").order_by("day")
        result = await self._session.execute(statement)
        return [
            (
                r[0] if isinstance(r[0], date) else date.fromisoformat(r[0]),
                int(r[1]),
                _to_float(r[2]),
            )
            for r in result.all()
        ]

    async def reservations_by_day(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters
    ) -> list[tuple[date, int]]:
        """Ticket count reserved on each day (RESERVED, PAID or WINNER all
        passed through a reservation, so all three count here)."""
        statement = select(func.date(col(Ticket.reserved_at)).label("day"), func.count()).where(
            col(Ticket.deleted_at).is_(None),
            Ticket.owner_id == owner_id,
            col(Ticket.status).in_(_COUNTED_TICKET_STATUSES),
            col(Ticket.reserved_at).is_not(None),
        )
        if filters.raffle_id is not None:
            statement = statement.where(Ticket.raffle_id == filters.raffle_id)
        if filters.collaborator_id is not None:
            statement = statement.where(Ticket.collaborator_id == filters.collaborator_id)
        if filters.start_date is not None:
            statement = statement.where(func.date(col(Ticket.reserved_at)) >= filters.start_date)
        if filters.end_date is not None:
            statement = statement.where(func.date(col(Ticket.reserved_at)) <= filters.end_date)
        statement = statement.group_by("day").order_by("day")
        result = await self._session.execute(statement)
        return [
            (r[0] if isinstance(r[0], date) else date.fromisoformat(r[0]), int(r[1]))
            for r in result.all()
        ]

    async def status_distribution(
        self, owner_id: uuid.UUID, filters: AnalyticsFilters
    ) -> dict[TicketStatus, int]:
        statement = select(Ticket.status, func.count()).where(
            col(Ticket.deleted_at).is_(None), Ticket.owner_id == owner_id
        )
        if filters.raffle_id is not None:
            statement = statement.where(Ticket.raffle_id == filters.raffle_id)
        if filters.collaborator_id is not None:
            statement = statement.where(Ticket.collaborator_id == filters.collaborator_id)
        if filters.start_date is not None:
            statement = statement.where(func.date(col(Ticket.reserved_at)) >= filters.start_date)
        if filters.end_date is not None:
            statement = statement.where(func.date(col(Ticket.reserved_at)) <= filters.end_date)
        statement = statement.group_by(col(Ticket.status))
        result = await self._session.execute(statement)
        return {TicketStatus(r[0]): int(r[1]) for r in result.all()}
