import uuid

from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.database.base import utcnow
from app.modules.collaborators.models import Collaborator

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
            base = base.where(Collaborator.raffle_id == raffle_id)
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
        statement = select(Collaborator).where(
            Collaborator.raffle_id == raffle_id, col(Collaborator.deleted_at).is_(None)
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
        """True if the collaborator exists, is not deleted, and belongs to the
        given raffle (and owner / active state when required)."""
        statement = select(Collaborator.id).where(
            Collaborator.id == collaborator_id,
            Collaborator.raffle_id == raffle_id,
            col(Collaborator.deleted_at).is_(None),
        )
        if owner_id is not None:
            statement = statement.where(Collaborator.owner_id == owner_id)
        if active_only:
            statement = statement.where(col(Collaborator.is_active).is_(True))
        result = await self._session.execute(statement)
        return result.scalars().first() is not None

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
