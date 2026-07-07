from fastapi import APIRouter, status

from app.core.responses import SuccessResponse
from app.modules.public.dependencies import PublicUseCasesDep
from app.modules.public.schemas import (
    PublicCollaboratorView,
    PublicRaffleView,
    PublicReserveRequest,
    PublicReserveResult,
    PublicTicketView,
)

router = APIRouter()


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


@router.get("/raffles/{slug}/tickets", response_model=SuccessResponse[list[PublicTicketView]])
async def list_public_tickets(
    slug: str, use_cases: PublicUseCasesDep
) -> SuccessResponse[list[PublicTicketView]]:
    tickets = await use_cases.list_tickets(slug)
    return SuccessResponse(message="Tickets retrieved.", data=tickets)


@router.post(
    "/raffles/{slug}/reserve",
    response_model=SuccessResponse[PublicReserveResult],
    status_code=status.HTTP_201_CREATED,
)
async def reserve_public_ticket(
    slug: str, payload: PublicReserveRequest, use_cases: PublicUseCasesDep
) -> SuccessResponse[PublicReserveResult]:
    result = await use_cases.reserve(slug, payload)
    return SuccessResponse(message="Ticket reserved successfully.", data=result)
