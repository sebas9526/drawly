import uuid

from app.modules.dashboard.repositories import DashboardRepository
from app.modules.dashboard.schemas import (
    DashboardOverview,
    RecentRaffle,
    RecentReservation,
)
from app.modules.dashboard.services import DashboardService


class DashboardUseCases:
    """Application layer: fetches aggregates via the repository and assembles the
    overview via the service. The overview is a single call so the frontend makes
    one request. Every query is scoped to the authenticated owner."""

    RECENT_LIMIT = 10

    def __init__(
        self,
        repository: DashboardRepository,
        owner_id: uuid.UUID,
        service: DashboardService | None = None,
    ) -> None:
        self._repository = repository
        self._owner_id = owner_id
        self._service = service or DashboardService()

    async def get_overview(self) -> DashboardOverview:
        raffle_aggregates = await self._repository.raffle_aggregates(self._owner_id)
        ticket_aggregates = await self._repository.ticket_aggregates(self._owner_id)
        participants = await self._repository.count_participants(self._owner_id)
        collaborators = await self._repository.count_collaborators(self._owner_id)
        recent_reservations = await self.get_recent_reservations()
        recent_raffles = await self.get_recent_raffles()

        return DashboardOverview(
            raffles=self._service.raffle_counts(raffle_aggregates),
            tickets=self._service.ticket_counts(ticket_aggregates),
            participants=participants,
            collaborators=collaborators,
            sales=self._service.sales(raffle_aggregates, ticket_aggregates),
            recent_reservations=recent_reservations,
            recent_raffles=recent_raffles,
        )

    async def get_recent_reservations(self) -> list[RecentReservation]:
        rows = await self._repository.recent_reservations(self.RECENT_LIMIT, self._owner_id)
        return [
            RecentReservation(
                number=number,
                reserved_at=reserved_at,
                raffle_title=raffle_title,
                participant_name=participant_name,
            )
            for (number, reserved_at, raffle_title, participant_name) in rows
        ]

    async def get_recent_raffles(self) -> list[RecentRaffle]:
        rows = await self._repository.recent_raffles(self.RECENT_LIMIT, self._owner_id)
        return [
            RecentRaffle(
                title=title,
                status=status,
                total_tickets=total_tickets,
                available_count=available_count,
            )
            for (title, status, total_tickets, available_count) in rows
        ]
