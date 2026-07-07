"""Pure unit tests for the dashboard assembly service (no DB)."""

from app.modules.dashboard.services import DashboardService
from app.modules.raffles.models import RaffleStatus
from app.modules.tickets.models import TicketStatus


def test_raffle_counts_totals_and_active() -> None:
    aggregates = {
        RaffleStatus.DRAFT: (2, 0.0),
        RaffleStatus.PUBLISHED: (3, 0.0),
        RaffleStatus.CLOSED: (1, 0.0),
    }
    counts = DashboardService.raffle_counts(aggregates)
    assert counts.total == 6
    assert counts.active == 5  # draft + published
    assert counts.draft == 2
    assert counts.published == 3
    assert counts.closed == 1
    assert counts.archived == 0


def test_ticket_counts_total_sums_all_statuses() -> None:
    aggregates = {
        TicketStatus.AVAILABLE: (10, 0.0),
        TicketStatus.RESERVED: (3, 0.0),
        TicketStatus.PAID: (2, 0.0),
        TicketStatus.CANCELLED: (1, 0.0),
    }
    counts = DashboardService.ticket_counts(aggregates)
    assert counts.total == 16
    assert counts.available == 10
    assert counts.reserved == 3
    assert counts.paid == 2


def test_sales_uses_potential_and_status_values() -> None:
    raffle_aggregates = {
        RaffleStatus.PUBLISHED: (1, 100000.0),
        RaffleStatus.DRAFT: (1, 30000.0),
    }
    ticket_aggregates = {
        TicketStatus.RESERVED: (2, 40000.0),
        TicketStatus.PAID: (1, 20000.0),
    }
    sales = DashboardService.sales(raffle_aggregates, ticket_aggregates)
    assert sales.potential_value == 130000.0
    assert sales.reserved_value == 40000.0
    assert sales.paid_value == 20000.0
