import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.pagination import build_pagination_meta, offset_for
from app.core.responses import PaginatedResponse, SuccessResponse
from app.modules.participants.dependencies import ParticipantUseCasesDep
from app.modules.participants.schemas import (
    ParticipantCreate,
    ParticipantRead,
    ParticipantUpdate,
)
from app.modules.tickets.schemas import TicketRead

router = APIRouter()


@router.post(
    "", response_model=SuccessResponse[ParticipantRead], status_code=status.HTTP_201_CREATED
)
async def create_participant(
    payload: ParticipantCreate, use_cases: ParticipantUseCasesDep
) -> SuccessResponse[ParticipantRead]:
    participant = await use_cases.create(payload)
    return SuccessResponse(message="Participant created successfully.", data=participant)


@router.get("", response_model=PaginatedResponse[ParticipantRead])
async def list_participants(
    use_cases: ParticipantUseCasesDep,
    search: Annotated[str | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[ParticipantRead]:
    participants, total = await use_cases.list_participants(
        search=search, offset=offset_for(page, page_size), limit=page_size
    )
    return PaginatedResponse(
        data=participants,
        pagination=build_pagination_meta(page=page, page_size=page_size, total=total),
    )


@router.get("/{participant_id}", response_model=SuccessResponse[ParticipantRead])
async def get_participant(
    participant_id: uuid.UUID, use_cases: ParticipantUseCasesDep
) -> SuccessResponse[ParticipantRead]:
    participant = await use_cases.get(participant_id)
    return SuccessResponse(message="Participant retrieved.", data=participant)


@router.patch("/{participant_id}", response_model=SuccessResponse[ParticipantRead])
async def update_participant(
    participant_id: uuid.UUID, payload: ParticipantUpdate, use_cases: ParticipantUseCasesDep
) -> SuccessResponse[ParticipantRead]:
    participant = await use_cases.update(participant_id, payload)
    return SuccessResponse(message="Participant updated.", data=participant)


@router.delete("/{participant_id}", response_model=SuccessResponse[dict[str, bool]])
async def delete_participant(
    participant_id: uuid.UUID, use_cases: ParticipantUseCasesDep
) -> SuccessResponse[dict[str, bool]]:
    await use_cases.delete(participant_id)
    return SuccessResponse(message="Participant deleted.", data={"deleted": True})


@router.get("/{participant_id}/tickets", response_model=SuccessResponse[list[TicketRead]])
async def get_participant_tickets(
    participant_id: uuid.UUID, use_cases: ParticipantUseCasesDep
) -> SuccessResponse[list[TicketRead]]:
    tickets = await use_cases.get_tickets(participant_id)
    return SuccessResponse(
        message="Participant tickets retrieved.",
        data=[TicketRead.from_entity(ticket) for ticket in tickets],
    )
