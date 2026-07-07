from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.raffles.repositories import RaffleRepository
from app.modules.raffles.services import TicketProvisioning
from app.modules.raffles.use_cases import RaffleUseCases
from app.modules.tickets.dependencies import get_ticket_provisioning
from app.modules.users.dependencies import CurrentUserDep


def get_raffle_use_cases(
    session: Annotated[AsyncSession, Depends(get_session)],
    tickets: Annotated[TicketProvisioning, Depends(get_ticket_provisioning)],
    current_user: CurrentUserDep,
) -> RaffleUseCases:
    """Admin surface: authenticated and owner-scoped."""
    return RaffleUseCases(
        session=session,
        repository=RaffleRepository(session),
        tickets=tickets,
        owner_id=current_user.id,
    )


def get_public_raffles(
    session: Annotated[AsyncSession, Depends(get_session)],
    tickets: Annotated[TicketProvisioning, Depends(get_ticket_provisioning)],
) -> RaffleUseCases:
    """Exposes RaffleUseCases as the public module's PublicRaffles port
    (published-raffle lookup by slug). Unscoped and unauthenticated on purpose."""
    return RaffleUseCases(
        session=session,
        repository=RaffleRepository(session),
        tickets=tickets,
    )


RaffleUseCasesDep = Annotated[RaffleUseCases, Depends(get_raffle_use_cases)]
