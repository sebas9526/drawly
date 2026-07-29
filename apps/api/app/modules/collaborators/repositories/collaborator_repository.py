import uuid
from collections.abc import Sequence

from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.database.base import utcnow
from app.modules.collaborators.models import Collaborator, CollaboratorRaffle
from app.modules.raffles.models import Raffle, RaffleStatus

# Whitelisted sort columns (avoids arbitrary/injected ORDER BY).
_SORT_COLUMNS = {
    "created_at": Collaborator.created_at,
    "name": Collaborator.name,
    "is_active": Collaborator.is_active,
}


class CollaboratorRepository:
    """Soft-delete-aware persistence for collaborators. Only DB access point for
    the module — no query logic leaks into services/use cases/routers."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, collaborator: Collaborator) -> Collaborator:
        self._session.add(collaborator)
        await self._session.flush()
        await self._session.refresh(collaborator)
        return collaborator

    async def get(
        self, collaborator_id: uuid.UUID, *, owner_id: uuid.UUID | None = None
    ) -> Collaborator | None:
        statement = select(Collaborator).where(
            Collaborator.id == collaborator_id, col(Collaborator.deleted_at).is_(None)
        )
        if owner_id is not None:
            statement = statement.where(Collaborator.owner_id == owner_id)
        result = await self._session.execute(statement)
        return result.scalars().first()

    async def list_paginated(
        self,
        *,
        search: str | None,
        raffle_id: uuid.UUID | None,
        is_active: bool | None,
        sort: str,
        order: str,
        offset: int,
        limit: int,
        owner_id: uuid.UUID | None = None,
    ) -> tuple[list[Collaborator], int]:
        base = select(Collaborator).where(col(Collaborator.deleted_at).is_(None))
        if owner_id is not None:
            base = base.where(Collaborator.owner_id == owner_id)
        if raffle_id is not None:
            base = base.join(
                CollaboratorRaffle, col(CollaboratorRaffle.collaborator_id) == Collaborator.id
            ).where(
                CollaboratorRaffle.raffle_id == raffle_id,
                col(CollaboratorRaffle.deleted_at).is_(None),
            )
        if is_active is not None:
            base = base.where(Collaborator.is_active == is_active)
        if search:
            pattern = f"%{search.strip()}%"
            base = base.where(
                or_(
                    col(Collaborator.name).ilike(pattern),
                    col(Collaborator.phone).ilike(pattern),
                    col(Collaborator.email).ilike(pattern),
                )
            )

        sort_col = _SORT_COLUMNS.get(sort, Collaborator.created_at)
        ordering = col(sort_col).asc() if order == "asc" else col(sort_col).desc()

        total = await self._session.execute(select(func.count()).select_from(base.subquery()))
        items = await self._session.execute(base.order_by(ordering).offset(offset).limit(limit))
        return list(items.scalars().all()), int(total.scalar_one())

    async def list_by_raffle(
        self,
        raffle_id: uuid.UUID,
        *,
        owner_id: uuid.UUID | None = None,
        active_only: bool = False,
    ) -> list[Collaborator]:
        statement = (
            select(Collaborator)
            .join(CollaboratorRaffle, col(CollaboratorRaffle.collaborator_id) == Collaborator.id)
            .where(
                CollaboratorRaffle.raffle_id == raffle_id,
                col(CollaboratorRaffle.deleted_at).is_(None),
                col(Collaborator.deleted_at).is_(None),
            )
        )
        if owner_id is not None:
            statement = statement.where(Collaborator.owner_id == owner_id)
        if active_only:
            statement = statement.where(col(Collaborator.is_active).is_(True))
        statement = statement.order_by(col(Collaborator.name).asc())
        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def exists_in_raffle(
        self,
        collaborator_id: uuid.UUID,
        raffle_id: uuid.UUID,
        *,
        owner_id: uuid.UUID | None = None,
        active_only: bool = False,
    ) -> bool:
        """True if the collaborator exists, is not deleted, and is linked to
        the given raffle (and owner / active state when required)."""
        statement = (
            select(Collaborator.id)
            .join(CollaboratorRaffle, col(CollaboratorRaffle.collaborator_id) == Collaborator.id)
            .where(
                Collaborator.id == collaborator_id,
                CollaboratorRaffle.raffle_id == raffle_id,
                col(CollaboratorRaffle.deleted_at).is_(None),
                col(Collaborator.deleted_at).is_(None),
            )
        )
        if owner_id is not None:
            statement = statement.where(Collaborator.owner_id == owner_id)
        if active_only:
            statement = statement.where(col(Collaborator.is_active).is_(True))
        result = await self._session.execute(statement)
        return result.scalars().first() is not None

    async def names_by_ids(self, collaborator_ids: Sequence[uuid.UUID]) -> dict[uuid.UUID, str]:
        """Batch name lookup — e.g. for the participants module to show who
        sold a ticket without exposing the full Collaborator entity."""
        ids = list(collaborator_ids)
        if not ids:
            return {}
        statement = select(Collaborator.id, Collaborator.name).where(
            col(Collaborator.id).in_(ids), col(Collaborator.deleted_at).is_(None)
        )
        result = await self._session.execute(statement)
        out: dict[uuid.UUID, str] = {}
        for collaborator_id, name in result.all():
            out[collaborator_id] = name
        return out

    async def list_raffle_ids_by_collaborators(
        self, collaborator_ids: Sequence[uuid.UUID]
    ) -> dict[uuid.UUID, list[uuid.UUID]]:
        """Batch lookup — avoids an N+1 when assembling a list of collaborators
        into CollaboratorRead (each needs its own raffle_ids)."""
        ids = list(collaborator_ids)
        if not ids:
            return {}
        statement = select(CollaboratorRaffle.collaborator_id, CollaboratorRaffle.raffle_id).where(
            col(CollaboratorRaffle.collaborator_id).in_(ids),
            col(CollaboratorRaffle.deleted_at).is_(None),
        )
        result = await self._session.execute(statement)
        out: dict[uuid.UUID, list[uuid.UUID]] = {cid: [] for cid in ids}
        for collaborator_id, raffle_id in result.all():
            out[collaborator_id].append(raffle_id)
        return out

    async def set_raffles(
        self, collaborator_id: uuid.UUID, raffle_ids: Sequence[uuid.UUID]
    ) -> None:
        """Replaces the collaborator's full set of raffle links: soft-deletes
        every current (non-deleted) link, then inserts a fresh row per id in
        ``raffle_ids``. Used by both create and update — always the whole
        set, never an incremental add/remove, so callers don't need to diff."""
        now = utcnow()
        existing = await self._session.execute(
            select(CollaboratorRaffle).where(
                CollaboratorRaffle.collaborator_id == collaborator_id,
                col(CollaboratorRaffle.deleted_at).is_(None),
            )
        )
        for link in existing.scalars().all():
            link.deleted_at = now
            link.updated_at = now
            self._session.add(link)
        for raffle_id in raffle_ids:
            self._session.add(
                CollaboratorRaffle(collaborator_id=collaborator_id, raffle_id=raffle_id)
            )
        await self._session.flush()

    async def set_collaborators_for_raffle(
        self, raffle_id: uuid.UUID, collaborator_ids: Sequence[uuid.UUID]
    ) -> None:
        """Replaces the raffle's full set of collaborator links: soft-deletes
        every current (non-deleted) link, then inserts a fresh row per id in
        ``collaborator_ids``. Mirror of ``set_raffles``, keyed by raffle
        instead of by collaborator — lets a raffle's collaborator set be
        edited from the raffle form without touching each collaborator's own
        other raffle links."""
        now = utcnow()
        existing = await self._session.execute(
            select(CollaboratorRaffle).where(
                CollaboratorRaffle.raffle_id == raffle_id,
                col(CollaboratorRaffle.deleted_at).is_(None),
            )
        )
        for link in existing.scalars().all():
            link.deleted_at = now
            link.updated_at = now
            self._session.add(link)
        for collaborator_id in collaborator_ids:
            self._session.add(
                CollaboratorRaffle(collaborator_id=collaborator_id, raffle_id=raffle_id)
            )
        await self._session.flush()

    async def list_published_raffles_for_collaborator(
        self, collaborator_id: uuid.UUID
    ) -> list[Raffle] | None:
        """None if the collaborator doesn't exist, is inactive, or is
        deleted — distinct from an empty list (exists, active, but currently
        linked to zero published raffles). Used by the public referral link."""
        collaborator = await self._session.execute(
            select(Collaborator.id).where(
                Collaborator.id == collaborator_id,
                col(Collaborator.deleted_at).is_(None),
                col(Collaborator.is_active).is_(True),
            )
        )
        if collaborator.scalars().first() is None:
            return None

        statement = (
            select(Raffle)
            .join(CollaboratorRaffle, col(CollaboratorRaffle.raffle_id) == Raffle.id)
            .where(
                CollaboratorRaffle.collaborator_id == collaborator_id,
                col(CollaboratorRaffle.deleted_at).is_(None),
                Raffle.status == RaffleStatus.PUBLISHED,
                col(Raffle.deleted_at).is_(None),
            )
            .order_by(col(Raffle.title).asc())
        )
        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def save(self, collaborator: Collaborator) -> Collaborator:
        collaborator.updated_at = utcnow()
        self._session.add(collaborator)
        await self._session.flush()
        await self._session.refresh(collaborator)
        return collaborator

    async def soft_delete(self, collaborator: Collaborator) -> None:
        now = utcnow()
        collaborator.deleted_at = now
        collaborator.updated_at = now
        self._session.add(collaborator)
        await self._session.flush()
