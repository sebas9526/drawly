from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.analytics.repositories import AnalyticsRepository
from app.modules.analytics.use_cases import AnalyticsUseCases
from app.modules.users.dependencies import CurrentUserDep


def get_analytics_use_cases(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: CurrentUserDep,
) -> AnalyticsUseCases:
    """Every analytics report is authenticated and owner-scoped — it only ever
    reflects the caller's own raffles, tickets, participants and collaborators."""
    return AnalyticsUseCases(
        repository=AnalyticsRepository(session),
        owner_id=current_user.id,
    )


AnalyticsUseCasesDep = Annotated[AnalyticsUseCases, Depends(get_analytics_use_cases)]
