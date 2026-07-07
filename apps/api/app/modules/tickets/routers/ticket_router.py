import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.core.pagination import build_pagination_meta, offset_for
from app.core.responses import PaginatedResponse, SuccessResponse
from app.modules.tickets.dependencies import TicketUseCasesDep
from app.modules.tickets.models import TicketStatus
from app.modules.tickets.schemas import (
    AssignParticipantRequest,
    ReserveTicketRequest,
    SetCollaboratorRequest,
    TicketRead,
)

router = APIRouter()


@router.get("", response_model=PaginatedResponse[TicketRead])
async def list_tickets(
    use_cases: TicketUseCasesDep,
    raffle_id: Annotated[uuid.UUID | None, Query()] = None,
    status: Annotated[TicketStatus | None, Query()] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[TicketRead]:
    tickets, total = await use_cases.list_tickets(
        raffle_id=raffle_id, status=status, offset=offset_for(page, page_size), limit=page_size
    )
    return PaginatedResponse(
        data=[TicketRead.from_entity(ticket) for ticket in tickets],
        pagination=build_pagination_meta(page=page, page_size=page_size, total=total),
    )


@router.get("/available", response_model=SuccessResponse[list[TicketRead]])
async def list_available_tickets(
    use_cases: TicketUseCasesDep,
    raffle_id: Annotated[uuid.UUID, Query()],
) -> SuccessResponse[list[TicketRead]]:
    tickets = await use_cases.list_available(raffle_id)
    return SuccessResponse(
        message="Available tickets retrieved.",
        data=[TicketRead.from_entity(ticket) for ticket in tickets],
    )


@router.get("/{ticket_id}", response_model=SuccessResponse[TicketRead])
async def get_ticket(
    ticket_id: uuid.UUID, use_cases: TicketUseCasesDep
) -> SuccessResponse[TicketRead]:
    ticket = await use_cases.get_ticket(ticket_id)
    return SuccessResponse(message="Ticket retrieved.", data=TicketRead.from_entity(ticket))


@router.patch("/{ticket_id}/reserve", response_model=SuccessResponse[TicketRead])
async def reserve_ticket(
    ticket_id: uuid.UUID, payload: ReserveTicketRequest, use_cases: TicketUseCasesDep
) -> SuccessResponse[TicketRead]:
    ticket = await use_cases.reserve_ticket(
        ticket_id, payload.participant_id, payload.collaborator_id
    )
    return SuccessResponse(message="Ticket reserved.", data=TicketRead.from_entity(ticket))


@router.patch("/{ticket_id}/collaborator", response_model=SuccessResponse[TicketRead])
async def set_ticket_collaborator(
    ticket_id: uuid.UUID, payload: SetCollaboratorRequest, use_cases: TicketUseCasesDep
) -> SuccessResponse[TicketRead]:
    ticket = await use_cases.set_collaborator(ticket_id, payload.collaborator_id)
    return SuccessResponse(
        message="Ticket collaborator updated.", data=TicketRead.from_entity(ticket)
    )


@router.patch("/{ticket_id}/cancel", response_model=SuccessResponse[TicketRead])
async def cancel_ticket_reservation(
    ticket_id: uuid.UUID, use_cases: TicketUseCasesDep
) -> SuccessResponse[TicketRead]:
    ticket = await use_cases.cancel_reservation(ticket_id)
    return SuccessResponse(message="Reservation cancelled.", data=TicketRead.from_entity(ticket))


@router.patch("/{ticket_id}/pay", response_model=SuccessResponse[TicketRead])
async def mark_ticket_as_paid(
    ticket_id: uuid.UUID, use_cases: TicketUseCasesDep
) -> SuccessResponse[TicketRead]:
    ticket = await use_cases.mark_as_paid(ticket_id)
    return SuccessResponse(message="Ticket marked as paid.", data=TicketRead.from_entity(ticket))


@router.patch("/{ticket_id}/participant", response_model=SuccessResponse[TicketRead])
async def assign_ticket_participant(
    ticket_id: uuid.UUID, payload: AssignParticipantRequest, use_cases: TicketUseCasesDep
) -> SuccessResponse[TicketRead]:
    ticket = await use_cases.assign_participant(ticket_id, payload.participant_id)
    return SuccessResponse(message="Participant assigned.", data=TicketRead.from_entity(ticket))


@router.delete("/{ticket_id}/participant", response_model=SuccessResponse[TicketRead])
async def remove_ticket_participant(
    ticket_id: uuid.UUID, use_cases: TicketUseCasesDep
) -> SuccessResponse[TicketRead]:
    ticket = await use_cases.unassign_participant(ticket_id)
    return SuccessResponse(
        message="Participant removed; ticket released.", data=TicketRead.from_entity(ticket)
    )
