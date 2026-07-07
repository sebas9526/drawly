import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Query, status

from app.core.pagination import build_pagination_meta, offset_for
from app.core.responses import PaginatedResponse, SuccessResponse
from app.modules.collaborators.dependencies import CollaboratorUseCasesDep
from app.modules.collaborators.schemas import (
    CollaboratorCreate,
    CollaboratorRead,
    CollaboratorStats,
    CollaboratorUpdate,
)

router = APIRouter()


@router.post(
    "", response_model=SuccessResponse[CollaboratorRead], status_code=status.HTTP_201_CREATED
)
async def create_collaborator(
    payload: CollaboratorCreate, use_cases: CollaboratorUseCasesDep
) -> SuccessResponse[CollaboratorRead]:
    collaborator = await use_cases.create(payload)
    return SuccessResponse(
        message="Collaborator created successfully.",
        data=CollaboratorRead.from_entity(collaborator),
    )


@router.get("", response_model=PaginatedResponse[CollaboratorRead])
async def list_collaborators(
    use_cases: CollaboratorUseCasesDep,
    search: Annotated[str | None, Query()] = None,
    raffle_id: Annotated[uuid.UUID | None, Query()] = None,
    is_active: Annotated[bool | None, Query()] = None,
    sort: Annotated[Literal["created_at", "name", "is_active"], Query()] = "created_at",
    order: Annotated[Literal["asc", "desc"], Query()] = "desc",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginatedResponse[CollaboratorRead]:
    collaborators, total = await use_cases.list_collaborators(
        search=search,
        raffle_id=raffle_id,
        is_active=is_active,
        sort=sort,
        order=order,
        offset=offset_for(page, page_size),
        limit=page_size,
    )
    return PaginatedResponse(
        data=[CollaboratorRead.from_entity(c) for c in collaborators],
        pagination=build_pagination_meta(page=page, page_size=page_size, total=total),
    )


@router.get("/raffle/{raffle_id}", response_model=SuccessResponse[list[CollaboratorRead]])
async def list_collaborators_by_raffle(
    raffle_id: uuid.UUID,
    use_cases: CollaboratorUseCasesDep,
    active_only: Annotated[bool, Query()] = False,
) -> SuccessResponse[list[CollaboratorRead]]:
    collaborators = await use_cases.list_by_raffle(raffle_id, active_only=active_only)
    return SuccessResponse(
        message="Collaborators retrieved.",
        data=[CollaboratorRead.from_entity(c) for c in collaborators],
    )


@router.get("/raffle/{raffle_id}/stats", response_model=SuccessResponse[list[CollaboratorStats]])
async def collaborator_stats_by_raffle(
    raffle_id: uuid.UUID, use_cases: CollaboratorUseCasesDep
) -> SuccessResponse[list[CollaboratorStats]]:
    stats = await use_cases.stats_by_raffle(raffle_id)
    return SuccessResponse(message="Collaborator stats retrieved.", data=stats)


@router.get("/{collaborator_id}", response_model=SuccessResponse[CollaboratorRead])
async def get_collaborator(
    collaborator_id: uuid.UUID, use_cases: CollaboratorUseCasesDep
) -> SuccessResponse[CollaboratorRead]:
    collaborator = await use_cases.get(collaborator_id)
    return SuccessResponse(
        message="Collaborator retrieved.", data=CollaboratorRead.from_entity(collaborator)
    )


@router.put("/{collaborator_id}", response_model=SuccessResponse[CollaboratorRead])
async def update_collaborator(
    collaborator_id: uuid.UUID, payload: CollaboratorUpdate, use_cases: CollaboratorUseCasesDep
) -> SuccessResponse[CollaboratorRead]:
    collaborator = await use_cases.update(collaborator_id, payload)
    return SuccessResponse(
        message="Collaborator updated.", data=CollaboratorRead.from_entity(collaborator)
    )


@router.patch("/{collaborator_id}/activate", response_model=SuccessResponse[CollaboratorRead])
async def activate_collaborator(
    collaborator_id: uuid.UUID, use_cases: CollaboratorUseCasesDep
) -> SuccessResponse[CollaboratorRead]:
    collaborator = await use_cases.set_active(collaborator_id, is_active=True)
    return SuccessResponse(
        message="Collaborator activated.", data=CollaboratorRead.from_entity(collaborator)
    )


@router.patch("/{collaborator_id}/deactivate", response_model=SuccessResponse[CollaboratorRead])
async def deactivate_collaborator(
    collaborator_id: uuid.UUID, use_cases: CollaboratorUseCasesDep
) -> SuccessResponse[CollaboratorRead]:
    collaborator = await use_cases.set_active(collaborator_id, is_active=False)
    return SuccessResponse(
        message="Collaborator deactivated.", data=CollaboratorRead.from_entity(collaborator)
    )


@router.delete("/{collaborator_id}", response_model=SuccessResponse[dict[str, bool]])
async def delete_collaborator(
    collaborator_id: uuid.UUID, use_cases: CollaboratorUseCasesDep
) -> SuccessResponse[dict[str, bool]]:
    await use_cases.delete(collaborator_id)
    return SuccessResponse(message="Collaborator deleted.", data={"deleted": True})
