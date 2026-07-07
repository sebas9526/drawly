import uuid

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.database.base import utcnow
from app.modules.raffles.models import Raffle


class RaffleRepository:
    """Soft-delete-aware persistence for raffles. The only place that talks to
    the DB for this module (no query logic leaks into services/routers)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, raffle: Raffle) -> Raffle:
        self._session.add(raffle)
        await self._session.flush()
        await self._session.refresh(raffle)
        return raffle

    async def get(
        self, raffle_id: uuid.UUID, *, owner_id: uuid.UUID | None = None
    ) -> Raffle | None:
        statement = select(Raffle).where(Raffle.id == raffle_id, col(Raffle.deleted_at).is_(None))
        if owner_id is not None:
            statement = statement.where(Raffle.owner_id == owner_id)
        result = await self._session.execute(statement)
        return result.scalars().first()

    async def list_paginated(
        self, *, offset: int, limit: int, owner_id: uuid.UUID | None = None
    ) -> tuple[list[Raffle], int]:
        base = select(Raffle).where(col(Raffle.deleted_at).is_(None))
        if owner_id is not None:
            base = base.where(Raffle.owner_id == owner_id)
        total = await self._session.execute(select(func.count()).select_from(base.subquery()))
        items = await self._session.execute(
            base.order_by(col(Raffle.created_at).desc()).offset(offset).limit(limit)
        )
        return list(items.scalars().all()), int(total.scalar_one())

    async def get_by_slug(self, slug: str) -> Raffle | None:
        statement = select(Raffle).where(
            Raffle.public_slug == slug, col(Raffle.deleted_at).is_(None)
        )
        result = await self._session.execute(statement)
        return result.scalars().first()

    async def exists_slug(self, slug: str) -> bool:
        statement = select(Raffle.id).where(
            Raffle.public_slug == slug, col(Raffle.deleted_at).is_(None)
        )
        result = await self._session.execute(statement)
        return result.scalars().first() is not None

    async def save(self, raffle: Raffle) -> Raffle:
        raffle.updated_at = utcnow()
        self._session.add(raffle)
        await self._session.flush()
        await self._session.refresh(raffle)
        return raffle
