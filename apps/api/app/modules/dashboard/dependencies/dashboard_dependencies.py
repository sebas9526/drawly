from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.dashboard.repositories import DashboardRepository
from app.modules.dashboard.use_cases import DashboardUseCases
from app.modules.users.dependencies import CurrentUserDep


def get_dashboard_use_cases(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: CurrentUserDep,
) -> DashboardUseCases:
    """Admin surface: authenticated and owner-scoped. The overview only ever
    reflects the caller's own raffles, tickets and participants."""
    return DashboardUseCases(
        repository=DashboardRepository(session),
        owner_id=current_user.id,
    )


DashboardUseCasesDep = Annotated[DashboardUseCases, Depends(get_dashboard_use_cases)]
