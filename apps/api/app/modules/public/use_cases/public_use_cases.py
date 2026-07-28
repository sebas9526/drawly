import uuid

from app.modules.public.exceptions import (
    PublicCollaboratorNotFoundError,
    PublicTicketNotFoundError,
)
from app.modules.public.schemas import (
    PublicCollaboratorView,
    PublicRaffleView,
    PublicReferralRaffleView,
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
from app.modules.raffles.models import RaffleStatus
from app.modules.tickets.models import TicketStatus


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

        winner_ticket_number: int | None = None
        winner_participant_name: str | None = None
        # winner_ticket_id also gets set on an *unresolved* attempt (the
        # entered number wasn't paid) — only announce it publicly once the
        # raffle actually closed with a confirmed winner.
        if raffle.status is RaffleStatus.CLOSED and raffle.winner_ticket_id is not None:
            winner_ticket = await self._tickets.get_by_id(raffle.winner_ticket_id)
            if winner_ticket is not None and winner_ticket.status is TicketStatus.WINNER:
                winner_ticket_number = winner_ticket.number
                if winner_ticket.participant_id is not None:
                    participant = await self._participants.get(winner_ticket.participant_id)
                    winner_participant_name = participant.full_name

        return PublicRaffleView.from_raffle(
            raffle,
            counts,
            winner_ticket_number=winner_ticket_number,
            winner_participant_name=winner_participant_name,
        )

    async def list_collaborators(self, slug: str) -> list[PublicCollaboratorView]:
        raffle = await self._raffles.get_published_by_slug(slug)
        collaborators = await self._collaborators.list_by_raffle(raffle.id, active_only=True)
        return [PublicCollaboratorView.from_collaborator(c) for c in collaborators]

    async def get_referral_raffles(
        self, collaborator_id: uuid.UUID
    ) -> list[PublicReferralRaffleView]:
        """A collaborator's personal referral link (/ref/{id}): their
        currently-published raffles, so the frontend can send the visitor
        straight to reserving (one raffle) or show a picker (several)."""
        raffles = await self._collaborators.list_published_raffles(collaborator_id)
        if raffles is None:
            raise PublicCollaboratorNotFoundError()
        return [PublicReferralRaffleView.from_raffle(raffle) for raffle in raffles]

    async def list_tickets(
        self, slug: str, *, offset: int, limit: int
    ) -> tuple[list[PublicTicketView], int]:
        raffle = await self._raffles.get_published_by_slug(slug)
        tickets, total = await self._tickets.list_by_raffle(raffle.id, offset=offset, limit=limit)
        return [PublicTicketView.from_ticket(ticket) for ticket in tickets], total

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
