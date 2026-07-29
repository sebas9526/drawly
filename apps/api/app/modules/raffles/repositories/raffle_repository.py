import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.database.base import utcnow
from app.modules.raffles.models import Raffle, RaffleStatus


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

    async def list_scheduled_to_publish(self, *, now: datetime, limit: int = 500) -> list[Raffle]:
        """DRAFT raffles whose ``publish_at`` has arrived, system-wide (no
        owner scoping — a schedule firing isn't a per-request concern).
        Row-locked so the sweep can't race a manual publish click. Bounded by
        ``limit`` per run so one tick can't block for too long if a large
        backlog ever accumulates (the next tick picks up the rest)."""
        statement = (
            select(Raffle)
            .where(
                Raffle.status == RaffleStatus.DRAFT,
                col(Raffle.publish_at).is_not(None),
                col(Raffle.publish_at) <= now,
                col(Raffle.deleted_at).is_(None),
            )
            .order_by(col(Raffle.publish_at).asc())
            .limit(limit)
            .with_for_update()
        )
        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def list_closed_past_cutoff(self, *, cutoff: datetime, limit: int = 500) -> list[Raffle]:
        """CLOSED raffles whose ``closed_at`` is at or before ``cutoff``
        (i.e. the grace period has elapsed), system-wide. Row-locked so the
        cleanup sweep can't race anything else touching the raffle. Bounded
        by ``limit`` per run, same reasoning as list_scheduled_to_publish."""
        statement = (
            select(Raffle)
            .where(
                Raffle.status == RaffleStatus.CLOSED,
                col(Raffle.closed_at).is_not(None),
                col(Raffle.closed_at) <= cutoff,
                col(Raffle.deleted_at).is_(None),
            )
            .order_by(col(Raffle.closed_at).asc())
            .limit(limit)
            .with_for_update()
        )
        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def save(self, raffle: Raffle) -> Raffle:
        raffle.updated_at = utcnow()
        self._session.add(raffle)
        await self._session.flush()
        await self._session.refresh(raffle)
        return raffle

    async def hard_delete(self, raffle: Raffle) -> None:
        """Permanently removes the raffle row — the organizer explicitly
        asked for "Eliminar rifa" to be a real delete, not the soft-delete
        every other module uses. Caller must have already cleared the
        raffle's own tickets (RaffleUseCases.delete) — collaborator_raffles
        links are handled by the DB itself (ON DELETE CASCADE, see migration
        0012)."""
        await self._session.delete(raffle)
        await self._session.flush()
