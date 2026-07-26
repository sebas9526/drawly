from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.config import get_settings
from app.core.pagination import build_pagination_meta, offset_for
from app.core.rate_limit import rate_limit
from app.core.responses import PaginatedResponse, SuccessResponse
from app.modules.public.dependencies import PublicUseCasesDep
from app.modules.public.schemas import (
    PublicCollaboratorView,
    PublicRaffleView,
    PublicReserveRequest,
    PublicReserveResult,
    PublicTicketView,
)

_settings = get_settings()
# Applies to every route in this router: the whole public portal is
# unauthenticated, so it all gets a baseline throttle.
_public_rate_limit = Depends(
    rate_limit(
        name="public",
        max_requests=_settings.rate_limit_public_max_requests,
        window_seconds=_settings.rate_limit_public_window_seconds,
    )
)
# Extra, stricter bucket stacked on top of the baseline one, only for the
# state-changing reservation endpoint.
_reserve_rate_limit = Depends(
    rate_limit(
        name="reserve",
        max_requests=_settings.rate_limit_reserve_max_requests,
        window_seconds=_settings.rate_limit_reserve_window_seconds,
    )
)

router = APIRouter(dependencies=[_public_rate_limit])


@router.get("/raffles/{slug}", response_model=SuccessResponse[PublicRaffleView])
async def get_public_raffle(
    slug: str, use_cases: PublicUseCasesDep
) -> SuccessResponse[PublicRaffleView]:
    raffle = await use_cases.get_raffle(slug)
    return SuccessResponse(message="Raffle retrieved.", data=raffle)


@router.get(
    "/raffles/{slug}/collaborators",
    response_model=SuccessResponse[list[PublicCollaboratorView]],
)
async def list_public_collaborators(
    slug: str, use_cases: PublicUseCasesDep
) -> SuccessResponse[list[PublicCollaboratorView]]:
    collaborators = await use_cases.list_collaborators(slug)
    return SuccessResponse(message="Collaborators retrieved.", data=collaborators)


@router.get("/raffles/{slug}/tickets", response_model=PaginatedResponse[PublicTicketView])
async def list_public_tickets(
    slug: str,
    use_cases: PublicUseCasesDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=1000)] = 1000,
) -> PaginatedResponse[PublicTicketView]:
    tickets, total = await use_cases.list_tickets(
        slug, offset=offset_for(page, page_size), limit=page_size
    )
    return PaginatedResponse(
        data=tickets, pagination=build_pagination_meta(page=page, page_size=page_size, total=total)
    )


@router.post(
    "/raffles/{slug}/reserve",
    response_model=SuccessResponse[PublicReserveResult],
    status_code=status.HTTP_201_CREATED,
    dependencies=[_reserve_rate_limit],
)
async def reserve_public_ticket(
    slug: str, payload: PublicReserveRequest, use_cases: PublicUseCasesDep
) -> SuccessResponse[PublicReserveResult]:
    result = await use_cases.reserve(slug, payload)
    return SuccessResponse(message="Ticket reserved successfully.", data=result)
