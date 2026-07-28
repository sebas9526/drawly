from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.session import get_session, get_session_factory
from app.modules.raffles.models import Raffle
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


async def sweep_scheduled_raffles() -> list[Raffle]:
    """System-wide job (no request scope): opens its own session, publishes
    every DRAFT raffle whose scheduled activation date has arrived (and that
    already has tickets), and returns what it touched. Wired into the app
    lifespan's periodic scheduler (see app/main.py) — not a route dependency,
    so it has no FastAPI ``Depends`` of its own."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        use_cases = RaffleUseCases(
            session=session,
            repository=RaffleRepository(session),
            tickets=get_ticket_provisioning(session),
        )
        return await use_cases.publish_scheduled_raffles()


async def sweep_closed_raffles() -> list[Raffle]:
    """System-wide job (no request scope): opens its own session, soft-deletes
    every CLOSED raffle (and its tickets) past its cleanup grace period, and
    returns what it touched. Wired into the app lifespan's periodic scheduler
    (see app/main.py) — not a route dependency."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        use_cases = RaffleUseCases(
            session=session,
            repository=RaffleRepository(session),
            tickets=get_ticket_provisioning(session),
        )
        return await use_cases.cleanup_closed_raffles(
            grace_hours=get_settings().raffle_cleanup_grace_hours
        )
