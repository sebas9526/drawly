"""Pure unit tests for AnalyticsService — no database, exercising the
assembly logic directly (percentages, rankings, per-status breakdowns)."""

import uuid
from datetime import UTC, datetime

from app.modules.analytics.services import AnalyticsService
from app.modules.raffles.models import RaffleStatus
from app.modules.tickets.models import TicketStatus


def test_executive_dashboard_computes_percentages_and_totals() -> None:
    raffle_aggregates = {
        RaffleStatus.DRAFT: (1, 10_000.0),
        RaffleStatus.PUBLISHED: (2, 50_000.0),
        RaffleStatus.CLOSED: (1, 20_000.0),
    }
    ticket_aggregates = {
        TicketStatus.AVAILABLE: (6, 0.0),
        TicketStatus.RESERVED: (2, 20_000.0),
        TicketStatus.PAID: (2, 20_000.0),
    }

    overview = AnalyticsService.executive_dashboard(
        raffle_aggregates, ticket_aggregates, participants_total=3, collaborators_total=2
    )

    assert overview.raffles_total == 4
    assert overview.raffles_published == 2
    assert overview.raffles_closed == 1
    assert overview.tickets_available == 6
    assert overview.tickets_reserved == 2
    assert overview.tickets_paid == 2
    assert overview.participants_total == 3
    assert overview.collaborators_total == 2
    assert overview.expected_revenue == 80_000.0
    assert overview.received_revenue == 20_000.0
    assert overview.percent_sold == 20.0  # 2 paid / 10 total
    assert overview.percent_reserved == 20.0


def test_executive_dashboard_handles_no_tickets_without_dividing_by_zero() -> None:
    overview = AnalyticsService.executive_dashboard(
        {}, {}, participants_total=0, collaborators_total=0
    )

    assert overview.percent_sold == 0.0
    assert overview.percent_reserved == 0.0
    assert overview.expected_revenue == 0.0


def test_raffle_report_row_derives_available_and_expected_revenue() -> None:
    raffle_id = uuid.uuid4()
    now = datetime.now(UTC)
    row = (raffle_id, "Rifa X", RaffleStatus.PUBLISHED, now, now, 100, 5_000.0, 20, 30)

    result = AnalyticsService.raffle_report_row(row)

    assert result.available == 50  # 100 - 20 reserved - 30 paid
    assert result.percent_sold == 30.0
    assert result.expected_revenue == 500_000.0  # 100 * 5000


def test_raffle_report_row_never_returns_negative_available() -> None:
    raffle_id = uuid.uuid4()
    now = datetime.now(UTC)
    # Pathological input (reserved+paid > total) must clamp, never go negative.
    row = (raffle_id, "Rifa Y", RaffleStatus.CLOSED, now, now, 10, 1_000.0, 8, 5)

    result = AnalyticsService.raffle_report_row(row)

    assert result.available == 0


def test_ranking_assigns_1_based_rank_preserving_repository_order() -> None:
    rows = [
        (uuid.uuid4(), "Top seller", 5, 500.0),
        (uuid.uuid4(), "Runner up", 3, 300.0),
    ]

    entries = AnalyticsService.ranking(rows)

    assert [entry.rank for entry in entries] == [1, 2]
    assert entries[0].name == "Top seller"
    assert entries[1].value == 300.0


def test_collaborator_report_rows_breaks_out_reserved_vs_paid() -> None:
    raffle_id = uuid.uuid4()
    collaborator_id = uuid.uuid4()
    rows = [
        (collaborator_id, "Pedro", raffle_id, "Rifa X", TicketStatus.RESERVED, 2, 20_000.0),
        (collaborator_id, "Pedro", raffle_id, "Rifa X", TicketStatus.PAID, 3, 30_000.0),
    ]

    result = AnalyticsService.collaborator_report_rows(
        rows,
        participants_served={collaborator_id: 4},
        raffle_total_tickets={raffle_id: 10},
    )

    assert len(result) == 1
    row = result[0]
    assert row.total_reservations == 2
    assert row.total_sales == 3
    assert row.participants_served == 4
    assert row.expected_amount == 50_000.0
    assert row.participation_percent == 30.0  # 3 paid / 10 total tickets
    assert row.rank == 1


def test_collaborator_report_rows_ranks_by_expected_amount_descending() -> None:
    raffle_id = uuid.uuid4()
    top = uuid.uuid4()
    second = uuid.uuid4()
    rows = [
        (second, "Segundo", raffle_id, "Rifa X", TicketStatus.PAID, 1, 10_000.0),
        (top, "Primero", raffle_id, "Rifa X", TicketStatus.PAID, 5, 50_000.0),
    ]

    result = AnalyticsService.collaborator_report_rows(
        rows, participants_served={}, raffle_total_tickets={raffle_id: 10}
    )

    assert [row.id for row in result] == [top, second]
    assert [row.rank for row in result] == [1, 2]


def test_participant_report_rows_tracks_last_purchase_and_totals() -> None:
    participant_id = uuid.uuid4()
    older = datetime(2026, 1, 1, tzinfo=UTC)
    newer = datetime(2026, 2, 1, tzinfo=UTC)
    rows = [
        (participant_id, "Ana", TicketStatus.PAID, 1, 10_000.0, older),
        (participant_id, "Ana", TicketStatus.PAID, 1, 10_000.0, newer),
        (participant_id, "Ana", TicketStatus.RESERVED, 1, 0.0, None),
    ]

    result = AnalyticsService.participant_report_rows(rows, raffles_count={participant_id: 2})

    assert len(result) == 1
    row = result[0]
    assert row.purchases_count == 2
    assert row.tickets_count == 3
    assert row.amount_invested == 20_000.0
    assert row.last_purchase_at == newer
    assert row.raffles_count == 2


def test_status_distribution_defaults_missing_statuses_to_zero() -> None:
    distribution = AnalyticsService.status_distribution({TicketStatus.PAID: 5})

    assert distribution.paid == 5
    assert distribution.available == 0
    assert distribution.reserved == 0
    assert distribution.cancelled == 0
    assert distribution.winner == 0
