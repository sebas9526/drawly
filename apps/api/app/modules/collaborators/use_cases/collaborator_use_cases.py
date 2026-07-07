import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.collaborators.exceptions import (
    CollaboratorNotFoundError,
    RaffleNotFoundForCollaboratorError,
)
from app.modules.collaborators.models import Collaborator
from app.modules.collaborators.repositories import CollaboratorRepository
from app.modules.collaborators.schemas import (
    CollaboratorCreate,
    CollaboratorStats,
    CollaboratorUpdate,
)
from app.modules.collaborators.services import (
    CollaboratorRaffles,
    CollaboratorService,
    CollaboratorTickets,
)


class CollaboratorUseCases:
    """Application layer for collaborators. Owns the transaction boundary and
    enforces ownership: every read/mutation is scoped to the authenticated owner,
    and creating a collaborator requires that the target raffle belongs to them.

    Also exposes the public listing (active collaborators of a raffle) via an
    unscoped instance — see the dependencies layer.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: CollaboratorRepository,
        raffles: CollaboratorRaffles,
        tickets: CollaboratorTickets,
        service: CollaboratorService | None = None,
        owner_id: uuid.UUID | None = None,
    ) -> None:
        self._session = session
        self._repository = repository
        self._raffles = raffles
        self._tickets = tickets
        self._service = service or CollaboratorService()
        self._owner_id = owner_id

    async def create(self, data: CollaboratorCreate) -> Collaborator:
        await self._require_owned_raffle(data.raffle_id)
        collaborator = self._service.build_collaborator(data, owner_id=self._owner_id)
        created = await self._repository.add(collaborator)
        await self._session.commit()
        return created

    async def get(self, collaborator_id: uuid.UUID) -> Collaborator:
        return await self._require(collaborator_id)

    async def list_collaborators(
        self,
        *,
        search: str | None,
        raffle_id: uuid.UUID | None,
        is_active: bool | None,
        sort: str,
        order: str,
        offset: int,
        limit: int,
    ) -> tuple[list[Collaborator], int]:
        return await self._repository.list_paginated(
            search=search,
            raffle_id=raffle_id,
            is_active=is_active,
            sort=sort,
            order=order,
            offset=offset,
            limit=limit,
            owner_id=self._owner_id,
        )

    async def list_by_raffle(
        self, raffle_id: uuid.UUID, *, active_only: bool = False
    ) -> list[Collaborator]:
        return await self._repository.list_by_raffle(
            raffle_id, owner_id=self._owner_id, active_only=active_only
        )

    async def update(self, collaborator_id: uuid.UUID, data: CollaboratorUpdate) -> Collaborator:
        collaborator = await self._require(collaborator_id)
        self._service.apply_update(collaborator, data)
        saved = await self._repository.save(collaborator)
        await self._session.commit()
        return saved

    async def set_active(self, collaborator_id: uuid.UUID, *, is_active: bool) -> Collaborator:
        collaborator = await self._require(collaborator_id)
        collaborator.is_active = is_active
        saved = await self._repository.save(collaborator)
        await self._session.commit()
        return saved

    async def delete(self, collaborator_id: uuid.UUID) -> None:
        collaborator = await self._require(collaborator_id)
        await self._repository.soft_delete(collaborator)
        await self._session.commit()

    async def stats_by_raffle(self, raffle_id: uuid.UUID) -> list[CollaboratorStats]:
        price = await self._require_owned_raffle(raffle_id)
        collaborators = await self._repository.list_by_raffle(raffle_id, owner_id=self._owner_id)
        counts = await self._tickets.counts_by_collaborator(raffle_id)
        stats: list[CollaboratorStats] = []
        for collaborator in collaborators:
            reserved, paid = counts.get(collaborator.id, (0, 0))
            total = reserved + paid
            stats.append(
                CollaboratorStats(
                    collaborator_id=collaborator.id,
                    name=collaborator.name,
                    color=collaborator.color,
                    reserved=reserved,
                    paid=paid,
                    total=total,
                    total_value=float(price) * total,
                )
            )
        return stats

    async def _require(self, collaborator_id: uuid.UUID) -> Collaborator:
        collaborator = await self._repository.get(collaborator_id, owner_id=self._owner_id)
        if collaborator is None:
            raise CollaboratorNotFoundError()
        return collaborator

    async def _require_owned_raffle(self, raffle_id: uuid.UUID) -> Decimal:
        """Return the raffle's ticket price, raising 404 if it doesn't exist or
        isn't owned by the current user."""
        if self._owner_id is None:
            raise RaffleNotFoundForCollaboratorError()
        price = await self._raffles.owned_raffle_price(raffle_id, self._owner_id)
        if price is None:
            raise RaffleNotFoundForCollaboratorError()
        return price
