import uuid
from collections.abc import Iterable, Sequence
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
    CollaboratorRead,
    CollaboratorStats,
    CollaboratorUpdate,
)
from app.modules.collaborators.services import (
    CollaboratorRaffles,
    CollaboratorService,
    CollaboratorTickets,
)
from app.modules.raffles.models import Raffle


class CollaboratorUseCases:
    """Application layer for collaborators. Owns the transaction boundary and
    enforces ownership: every read/mutation is scoped to the authenticated owner,
    and creating/updating a collaborator requires that every target raffle
    belongs to them.

    Read methods return fully-assembled ``CollaboratorRead`` (not the bare
    entity) since a collaborator's raffle_ids live in a separate join table —
    assembling them here (one batched lookup, no N+1) keeps that detail out of
    the router. Also exposes the public listing (active collaborators of a
    raffle, and a collaborator's published raffles for the referral link) via
    an unscoped instance — see the dependencies layer.
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

    async def create(self, data: CollaboratorCreate) -> CollaboratorRead:
        await self._require_owned_raffles(data.raffle_ids)
        collaborator = self._service.build_collaborator(data, owner_id=self._owner_id)
        created = await self._repository.add(collaborator)
        await self._repository.set_raffles(created.id, data.raffle_ids)
        await self._session.commit()
        return CollaboratorRead.from_entity(created, data.raffle_ids)

    async def get(self, collaborator_id: uuid.UUID) -> CollaboratorRead:
        collaborator = await self._require(collaborator_id)
        return await self._to_read(collaborator)

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
    ) -> tuple[list[CollaboratorRead], int]:
        collaborators, total = await self._repository.list_paginated(
            search=search,
            raffle_id=raffle_id,
            is_active=is_active,
            sort=sort,
            order=order,
            offset=offset,
            limit=limit,
            owner_id=self._owner_id,
        )
        return await self._to_read_many(collaborators), total

    async def list_by_raffle(
        self, raffle_id: uuid.UUID, *, active_only: bool = False
    ) -> list[CollaboratorRead]:
        collaborators = await self._repository.list_by_raffle(
            raffle_id, owner_id=self._owner_id, active_only=active_only
        )
        return await self._to_read_many(collaborators)

    async def update(
        self, collaborator_id: uuid.UUID, data: CollaboratorUpdate
    ) -> CollaboratorRead:
        collaborator = await self._require(collaborator_id)
        self._service.apply_update(collaborator, data)
        saved = await self._repository.save(collaborator)
        if data.raffle_ids is not None:
            # Only newly-added ids need the ownership check — an id that was
            # already linked stays valid even if it can no longer pass that
            # check today (e.g. a legacy raffle with no owner_id from before
            # auth existed). Re-validating unchanged links on every edit was
            # a real bug: it made a collaborator with one such link
            # permanently un-editable, even for unrelated fields.
            current = await self._repository.list_raffle_ids_by_collaborators([collaborator_id])
            added = set(data.raffle_ids) - set(current.get(collaborator_id, []))
            await self._require_owned_raffles(added)
            await self._repository.set_raffles(collaborator_id, data.raffle_ids)
        await self._session.commit()
        return await self._to_read(saved)

    async def set_active(self, collaborator_id: uuid.UUID, *, is_active: bool) -> CollaboratorRead:
        collaborator = await self._require(collaborator_id)
        collaborator.is_active = is_active
        saved = await self._repository.save(collaborator)
        await self._session.commit()
        return await self._to_read(saved)

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

    async def set_for_raffle(
        self, raffle_id: uuid.UUID, collaborator_ids: Sequence[uuid.UUID]
    ) -> list[CollaboratorRead]:
        """Replaces the full set of collaborators linked to a raffle — the
        mirror of ``update``'s ``raffle_ids`` handling, but driven from the
        raffle side (used by the raffle form, so organizers don't have to
        open each collaborator individually to link it)."""
        await self._require_owned_raffle(raffle_id)
        for collaborator_id in collaborator_ids:
            await self._require(collaborator_id)
        await self._repository.set_collaborators_for_raffle(raffle_id, collaborator_ids)
        await self._session.commit()
        return await self.list_by_raffle(raffle_id)

    async def names_by_ids(self, collaborator_ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, str]:
        """ParticipantCollaborators port: resolves seller names for the
        participants admin table."""
        return await self._repository.names_by_ids(collaborator_ids)

    async def list_published_raffles(self, collaborator_id: uuid.UUID) -> list[Raffle] | None:
        """PublicCollaborators port: a collaborator's published raffles, for
        the personal referral link. None if the collaborator doesn't exist,
        is inactive, or is deleted."""
        return await self._repository.list_published_raffles_for_collaborator(collaborator_id)

    async def _to_read(self, collaborator: Collaborator) -> CollaboratorRead:
        raffle_ids = await self._repository.list_raffle_ids_by_collaborators([collaborator.id])
        return CollaboratorRead.from_entity(collaborator, raffle_ids.get(collaborator.id, []))

    async def _to_read_many(self, collaborators: Sequence[Collaborator]) -> list[CollaboratorRead]:
        raffle_ids = await self._repository.list_raffle_ids_by_collaborators(
            [c.id for c in collaborators]
        )
        return [CollaboratorRead.from_entity(c, raffle_ids.get(c.id, [])) for c in collaborators]

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

    async def _require_owned_raffles(self, raffle_ids: Iterable[uuid.UUID]) -> None:
        for raffle_id in raffle_ids:
            await self._require_owned_raffle(raffle_id)
