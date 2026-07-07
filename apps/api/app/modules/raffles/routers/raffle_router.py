import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.pagination import build_pagination_meta, offset_for
from app.core.responses import PaginatedResponse, SuccessResponse
from app.modules.raffles.dependencies import RaffleUseCasesDep
from app.modules.raffles.schemas import (
    GenerateTicketsResult,
    RaffleCreate,
    RaffleRead,
    RaffleUpdate,
)

router = APIRouter()


@router.post(
    "",
    response_model=SuccessResponse[RaffleRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_raffle(
    payload: RaffleCreate, use_cases: RaffleUseCasesDep
) -> SuccessResponse[RaffleRead]:
    raffle = await use_cases.create(payload)
    return SuccessResponse(
        message="Raffle created successfully.", data=RaffleRead.from_entity(raffle)
    )


@router.get("", response_model=PaginatedResponse[RaffleRead])
async def list_raffles(
    use_cases: RaffleUseCasesDep,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[RaffleRead]:
    raffles, total = await use_cases.list_raffles(
        offset=offset_for(page, page_size), limit=page_size
    )
    return PaginatedResponse(
        data=[RaffleRead.from_entity(raffle) for raffle in raffles],
        pagination=build_pagination_meta(page=page, page_size=page_size, total=total),
    )


@router.get("/{raffle_id}", response_model=SuccessResponse[RaffleRead])
async def get_raffle(
    raffle_id: uuid.UUID, use_cases: RaffleUseCasesDep
) -> SuccessResponse[RaffleRead]:
    raffle = await use_cases.get(raffle_id)
    return SuccessResponse(message="Raffle retrieved.", data=RaffleRead.from_entity(raffle))


@router.put("/{raffle_id}", response_model=SuccessResponse[RaffleRead])
async def update_raffle(
    raffle_id: uuid.UUID, payload: RaffleUpdate, use_cases: RaffleUseCasesDep
) -> SuccessResponse[RaffleRead]:
    raffle = await use_cases.update(raffle_id, payload)
    return SuccessResponse(message="Raffle updated.", data=RaffleRead.from_entity(raffle))


@router.post(
    "/{raffle_id}/tickets",
    response_model=SuccessResponse[GenerateTicketsResult],
    status_code=status.HTTP_201_CREATED,
)
async def generate_raffle_tickets(
    raffle_id: uuid.UUID, use_cases: RaffleUseCasesDep
) -> SuccessResponse[GenerateTicketsResult]:
    generated = await use_cases.generate_tickets(raffle_id)
    return SuccessResponse(
        message="Tickets generated successfully.",
        data=GenerateTicketsResult(raffle_id=raffle_id, generated=generated),
    )


@router.patch("/{raffle_id}/publish", response_model=SuccessResponse[RaffleRead])
async def publish_raffle(
    raffle_id: uuid.UUID, use_cases: RaffleUseCasesDep
) -> SuccessResponse[RaffleRead]:
    raffle = await use_cases.publish(raffle_id)
    return SuccessResponse(message="Raffle published.", data=RaffleRead.from_entity(raffle))
