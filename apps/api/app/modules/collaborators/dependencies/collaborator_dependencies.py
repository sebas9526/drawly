import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.collaborators.repositories import CollaboratorRepository
from app.modules.collaborators.use_cases import CollaboratorUseCases
from app.modules.raffles.repositories import RaffleRepository
from app.modules.tickets.repositories import TicketRepository
from app.modules.users.dependencies import CurrentUserDep


class _RaffleOwnershipAdapter:
    """Satisfies CollaboratorRaffles using the raffles repository (composition
    root wiring — keeps the collaborators domain decoupled from raffles)."""

    def __init__(self, raffles: RaffleRepository) -> None:
        self._raffles = raffles

    async def owned_raffle_price(self, raffle_id: uuid.UUID, owner_id: uuid.UUID) -> Decimal | None:
        raffle = await self._raffles.get(raffle_id, owner_id=owner_id)
        return raffle.ticket_price if raffle is not None else None


class _CollaboratorTicketsAdapter:
    """Satisfies CollaboratorTickets using the tickets repository."""

    def __init__(self, tickets: TicketRepository) -> None:
        self._tickets = tickets

    async def counts_by_collaborator(
        self, raffle_id: uuid.UUID
    ) -> dict[uuid.UUID, tuple[int, int]]:
        return await self._tickets.counts_by_collaborator(raffle_id)


def _build(session: AsyncSession, owner_id: uuid.UUID | None) -> CollaboratorUseCases:
    return CollaboratorUseCases(
        session=session,
        repository=CollaboratorRepository(session),
        raffles=_RaffleOwnershipAdapter(RaffleRepository(session)),
        tickets=_CollaboratorTicketsAdapter(TicketRepository(session)),
        owner_id=owner_id,
    )


def get_collaborator_use_cases(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: CurrentUserDep,
) -> CollaboratorUseCases:
    """Admin surface: authenticated and owner-scoped."""
    return _build(session, current_user.id)


def get_public_collaborators(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CollaboratorUseCases:
    """Exposes CollaboratorUseCases (unscoped) for the public portal's active
    collaborator listing. The published raffle bounds access."""
    return _build(session, None)


CollaboratorUseCasesDep = Annotated[CollaboratorUseCases, Depends(get_collaborator_use_cases)]
