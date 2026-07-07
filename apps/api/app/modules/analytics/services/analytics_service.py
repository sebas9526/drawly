"""Pure assembly of analytics aggregates into response schemas. No I/O, so
every derivation here (percentages, rankings, per-status breakdowns) is
unit-testable without a database — the same split as
`app.modules.dashboard.services.DashboardService`."""

import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from app.modules.analytics.schemas import (
    CollaboratorReportRow,
    ExecutiveDashboard,
    ParticipantReportRow,
    RaffleReportRow,
    RankingEntry,
    TicketStatusDistribution,
)
from app.modules.raffles.models import RaffleStatus
from app.modules.tickets.models import TicketStatus

RaffleAgg = dict[RaffleStatus, tuple[int, float]]
TicketAgg = dict[TicketStatus, tuple[int, float]]

RaffleRow = tuple[uuid.UUID, str, RaffleStatus, datetime, datetime, int, float, int, int]
CollaboratorRow = tuple[uuid.UUID, str, uuid.UUID, str, TicketStatus | None, int, float]
ParticipantRow = tuple[uuid.UUID, str, TicketStatus | None, int, float, datetime | None]
RankingRow = tuple[uuid.UUID, str, int, float]


class AnalyticsService:
    # ------------------------------------------------------------------
    # Executive dashboard
    # ------------------------------------------------------------------

    @staticmethod
    def executive_dashboard(
        raffle_aggregates: RaffleAgg,
        ticket_aggregates: TicketAgg,
        participants_total: int,
        collaborators_total: int,
    ) -> ExecutiveDashboard:
        def raffle_count(status: RaffleStatus) -> int:
            return raffle_aggregates.get(status, (0, 0.0))[0]

        def ticket_count(status: TicketStatus) -> int:
            return ticket_aggregates.get(status, (0, 0.0))[0]

        tickets_total = sum(value[0] for value in ticket_aggregates.values())
        tickets_reserved = ticket_count(TicketStatus.RESERVED)
        tickets_paid = ticket_count(TicketStatus.PAID)

        return ExecutiveDashboard(
            raffles_total=sum(value[0] for value in raffle_aggregates.values()),
            raffles_published=raffle_count(RaffleStatus.PUBLISHED),
            raffles_closed=raffle_count(RaffleStatus.CLOSED),
            tickets_available=ticket_count(TicketStatus.AVAILABLE),
            tickets_reserved=tickets_reserved,
            tickets_paid=tickets_paid,
            participants_total=participants_total,
            collaborators_total=collaborators_total,
            expected_revenue=sum(value[1] for value in raffle_aggregates.values()),
            received_revenue=ticket_aggregates.get(TicketStatus.PAID, (0, 0.0))[1],
            percent_sold=(tickets_paid / tickets_total * 100) if tickets_total else 0.0,
            percent_reserved=(tickets_reserved / tickets_total * 100) if tickets_total else 0.0,
        )

    # ------------------------------------------------------------------
    # Raffle report
    # ------------------------------------------------------------------

    @staticmethod
    def raffle_report_row(row: RaffleRow) -> RaffleReportRow:
        raffle_id, title, status, created_at, draw_date, total, price, reserved, paid = row
        available = max(total - reserved - paid, 0)
        return RaffleReportRow(
            id=raffle_id,
            title=title,
            status=status,
            created_at=created_at,
            draw_date=draw_date,
            total_tickets=total,
            available=available,
            reserved=reserved,
            paid=paid,
            percent_sold=(paid / total * 100) if total else 0.0,
            expected_revenue=total * price,
        )

    @staticmethod
    def ranking(rows: Sequence[RankingRow]) -> list[RankingEntry]:
        """Rows must already be sorted by relevance (the repository orders by
        value DESC) — this only attaches a 1-based rank."""
        return [
            RankingEntry(id=row[0], name=row[1], count=row[2], value=row[3], rank=index + 1)
            for index, row in enumerate(rows)
        ]

    # ------------------------------------------------------------------
    # Collaborator report
    # ------------------------------------------------------------------

    @staticmethod
    def collaborator_report_rows(
        rows: Sequence[CollaboratorRow],
        participants_served: dict[uuid.UUID, int],
        raffle_total_tickets: dict[uuid.UUID, int],
    ) -> list[CollaboratorReportRow]:
        """Groups the (collaborator, status) rows from the repository into one
        row per collaborator, then ranks by expected amount descending."""

        @dataclass
        class _Accumulator:
            name: str
            raffle_id: uuid.UUID
            raffle_title: str
            reserved: int = 0
            paid: int = 0
            amount: float = 0.0

        by_collaborator: dict[uuid.UUID, _Accumulator] = {}
        for collaborator_id, name, raffle_id, raffle_title, status, count, value in rows:
            entry = by_collaborator.setdefault(
                collaborator_id,
                _Accumulator(name=name, raffle_id=raffle_id, raffle_title=raffle_title),
            )
            if status is TicketStatus.RESERVED:
                entry.reserved += count
                entry.amount += value
            elif status is TicketStatus.PAID:
                entry.paid += count
                entry.amount += value

        rows_with_share = [
            (
                collaborator_id,
                entry,
                (
                    entry.paid / raffle_total_tickets[entry.raffle_id] * 100
                    if raffle_total_tickets.get(entry.raffle_id)
                    else 0.0
                ),
            )
            for collaborator_id, entry in by_collaborator.items()
        ]
        rows_with_share.sort(key=lambda item: item[1].amount, reverse=True)

        return [
            CollaboratorReportRow(
                id=collaborator_id,
                name=entry.name,
                raffle_id=entry.raffle_id,
                raffle_title=entry.raffle_title,
                total_reservations=entry.reserved,
                total_sales=entry.paid,
                participants_served=participants_served.get(collaborator_id, 0),
                expected_amount=entry.amount,
                participation_percent=participation,
                rank=rank,
            )
            for rank, (collaborator_id, entry, participation) in enumerate(rows_with_share, start=1)
        ]

    # ------------------------------------------------------------------
    # Participant report
    # ------------------------------------------------------------------

    @staticmethod
    def participant_report_rows(
        rows: Sequence[ParticipantRow],
        raffles_count: dict[uuid.UUID, int],
    ) -> list[ParticipantReportRow]:
        @dataclass
        class _Accumulator:
            full_name: str
            tickets: int = 0
            purchases: int = 0
            invested: float = 0.0
            last_purchase_at: datetime | None = None

        by_participant: dict[uuid.UUID, _Accumulator] = {}
        for participant_id, full_name, status, count, value, sold_at in rows:
            entry = by_participant.setdefault(participant_id, _Accumulator(full_name=full_name))
            if status is not None:
                entry.tickets += count
            if status is TicketStatus.PAID:
                entry.purchases += count
                entry.invested += value
                if sold_at is not None and (
                    entry.last_purchase_at is None or sold_at > entry.last_purchase_at
                ):
                    entry.last_purchase_at = sold_at

        return [
            ParticipantReportRow(
                id=participant_id,
                full_name=entry.full_name,
                purchases_count=entry.purchases,
                tickets_count=entry.tickets,
                amount_invested=entry.invested,
                last_purchase_at=entry.last_purchase_at,
                raffles_count=raffles_count.get(participant_id, 0),
            )
            for participant_id, entry in by_participant.items()
        ]

    # ------------------------------------------------------------------
    # Global reports
    # ------------------------------------------------------------------

    @staticmethod
    def status_distribution(counts: dict[TicketStatus, int]) -> TicketStatusDistribution:
        return TicketStatusDistribution(
            available=counts.get(TicketStatus.AVAILABLE, 0),
            reserved=counts.get(TicketStatus.RESERVED, 0),
            paid=counts.get(TicketStatus.PAID, 0),
            cancelled=counts.get(TicketStatus.CANCELLED, 0),
            winner=counts.get(TicketStatus.WINNER, 0),
        )
