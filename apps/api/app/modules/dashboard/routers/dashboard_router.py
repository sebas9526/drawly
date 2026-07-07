from fastapi import APIRouter

from app.core.responses import SuccessResponse
from app.modules.dashboard.dependencies import DashboardUseCasesDep
from app.modules.dashboard.schemas import (
    DashboardOverview,
    RecentRaffle,
    RecentReservation,
)

router = APIRouter()


@router.get("/overview", response_model=SuccessResponse[DashboardOverview])
async def get_overview(use_cases: DashboardUseCasesDep) -> SuccessResponse[DashboardOverview]:
    overview = await use_cases.get_overview()
    return SuccessResponse(message="Dashboard overview.", data=overview)


@router.get("/reservations", response_model=SuccessResponse[list[RecentReservation]])
async def get_recent_reservations(
    use_cases: DashboardUseCasesDep,
) -> SuccessResponse[list[RecentReservation]]:
    reservations = await use_cases.get_recent_reservations()
    return SuccessResponse(message="Recent reservations.", data=reservations)


@router.get("/raffles", response_model=SuccessResponse[list[RecentRaffle]])
async def get_recent_raffles(
    use_cases: DashboardUseCasesDep,
) -> SuccessResponse[list[RecentRaffle]]:
    raffles = await use_cases.get_recent_raffles()
    return SuccessResponse(message="Recent raffles.", data=raffles)
