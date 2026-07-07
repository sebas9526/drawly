"""Pure assembly of dashboard aggregates into the response schema. No I/O, so
the derivations (totals, active count, sales) are unit-testable without a DB."""

from app.modules.dashboard.schemas import RaffleCounts, SalesSummary, TicketCounts
from app.modules.raffles.models import RaffleStatus
from app.modules.tickets.models import TicketStatus

RaffleAgg = dict[RaffleStatus, tuple[int, float]]
TicketAgg = dict[TicketStatus, tuple[int, float]]


class DashboardService:
    @staticmethod
    def raffle_counts(aggregates: RaffleAgg) -> RaffleCounts:
        def count(status: RaffleStatus) -> int:
            return aggregates.get(status, (0, 0.0))[0]

        draft = count(RaffleStatus.DRAFT)
        published = count(RaffleStatus.PUBLISHED)
        closed = count(RaffleStatus.CLOSED)
        archived = count(RaffleStatus.ARCHIVED)
        return RaffleCounts(
            total=draft + published + closed + archived,
            active=draft + published,
            draft=draft,
            published=published,
            closed=closed,
            archived=archived,
        )

    @staticmethod
    def ticket_counts(aggregates: TicketAgg) -> TicketCounts:
        def count(status: TicketStatus) -> int:
            return aggregates.get(status, (0, 0.0))[0]

        return TicketCounts(
            total=sum(value[0] for value in aggregates.values()),
            available=count(TicketStatus.AVAILABLE),
            reserved=count(TicketStatus.RESERVED),
            paid=count(TicketStatus.PAID),
        )

    @staticmethod
    def sales(raffle_aggregates: RaffleAgg, ticket_aggregates: TicketAgg) -> SalesSummary:
        return SalesSummary(
            potential_value=sum(value[1] for value in raffle_aggregates.values()),
            reserved_value=ticket_aggregates.get(TicketStatus.RESERVED, (0, 0.0))[1],
            paid_value=ticket_aggregates.get(TicketStatus.PAID, (0, 0.0))[1],
        )
