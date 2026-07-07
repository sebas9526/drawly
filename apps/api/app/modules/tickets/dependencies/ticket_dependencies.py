from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.collaborators.repositories import CollaboratorRepository
from app.modules.tickets.repositories import TicketRepository
from app.modules.tickets.use_cases import TicketUseCases
from app.modules.users.dependencies import CurrentUserDep


def get_ticket_use_cases(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: CurrentUserDep,
) -> TicketUseCases:
    """Admin surface: authenticated and owner-scoped. Every read/mutation is
    restricted to the caller's tickets."""
    return TicketUseCases(
        session=session,
        repository=TicketRepository(session),
        owner_id=current_user.id,
        collaborators=CollaboratorRepository(session),
    )


def _unscoped_ticket_use_cases(session: AsyncSession) -> TicketUseCases:
    """Ports used from other modules' already-scoped contexts (owner_id=None)."""
    return TicketUseCases(
        session=session,
        repository=TicketRepository(session),
        collaborators=CollaboratorRepository(session),
    )


def get_ticket_provisioning(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TicketUseCases:
    """Exposes TicketUseCases as the raffles module's TicketProvisioning port.

    Unscoped: the raffle use case supplies the owner explicitly when generating
    tickets (the raffle it belongs to is already ownership-verified).
    """
    return _unscoped_ticket_use_cases(session)


def get_participant_tickets(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TicketUseCases:
    """Exposes TicketUseCases as the participants module's ParticipantTickets
    port. Scoping is by participant_id, which already implies the owner."""
    return _unscoped_ticket_use_cases(session)


def get_public_tickets(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TicketUseCases:
    """Exposes TicketUseCases as the public module's PublicTickets port. Public
    reservation must not require auth; the published raffle bounds access."""
    return _unscoped_ticket_use_cases(session)


TicketUseCasesDep = Annotated[TicketUseCases, Depends(get_ticket_use_cases)]
