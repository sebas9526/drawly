from app.modules.public.exceptions import PublicTicketNotFoundError
from app.modules.public.schemas import (
    PublicCollaboratorView,
    PublicRaffleView,
    PublicReserveRequest,
    PublicReserveResult,
    PublicTicketView,
)
from app.modules.public.services import (
    PublicCollaborators,
    PublicParticipants,
    PublicRaffles,
    PublicTickets,
)


class PublicRaffleUseCases:
    """Application layer for the public portal. Orchestrates the raffles,
    tickets, participants and collaborators modules through ports; contains no
    persistence of its own. Every state rule (availability, reservation) stays in
    the tickets domain — the backend remains the source of truth."""

    def __init__(
        self,
        raffles: PublicRaffles,
        tickets: PublicTickets,
        participants: PublicParticipants,
        collaborators: PublicCollaborators,
    ) -> None:
        self._raffles = raffles
        self._tickets = tickets
        self._participants = participants
        self._collaborators = collaborators

    async def get_raffle(self, slug: str) -> PublicRaffleView:
        raffle = await self._raffles.get_published_by_slug(slug)
        counts = await self._tickets.status_counts(raffle.id)
        return PublicRaffleView.from_raffle(raffle, counts)

    async def list_collaborators(self, slug: str) -> list[PublicCollaboratorView]:
        raffle = await self._raffles.get_published_by_slug(slug)
        collaborators = await self._collaborators.list_by_raffle(raffle.id, active_only=True)
        return [PublicCollaboratorView.from_collaborator(c) for c in collaborators]

    async def list_tickets(self, slug: str) -> list[PublicTicketView]:
        raffle = await self._raffles.get_published_by_slug(slug)
        tickets = await self._tickets.list_by_raffle(raffle.id)
        return [PublicTicketView.from_ticket(ticket) for ticket in tickets]

    async def reserve(self, slug: str, request: PublicReserveRequest) -> PublicReserveResult:
        raffle = await self._raffles.get_published_by_slug(slug)
        ticket = await self._tickets.get_by_number(raffle.id, request.ticket_number)
        if ticket is None:
            raise PublicTicketNotFoundError()

        # Reuse-or-create the participant, then reserve. The tickets domain
        # rejects a non-available ticket (409), so a race to the same ticket
        # yields a clear error rather than a double reservation.
        participant = await self._participants.find_or_create(
            request.to_participant_create(), owner_id=raffle.owner_id
        )
        reserved = await self._tickets.reserve_ticket(
            ticket.id, participant.id, request.collaborator_id
        )

        return PublicReserveResult(
            ticket_number=reserved.number,
            raffle_title=raffle.title,
            status=reserved.status,
        )
