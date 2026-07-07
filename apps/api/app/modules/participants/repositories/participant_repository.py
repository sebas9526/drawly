import uuid

from sqlalchemy import func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.database.base import utcnow
from app.modules.participants.models import Participant


class ParticipantRepository:
    """Soft-delete-aware persistence for participants. Only DB access point for
    the module — no query logic leaks into services/use cases/routers."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, participant: Participant) -> Participant:
        self._session.add(participant)
        await self._session.flush()
        await self._session.refresh(participant)
        return participant

    async def get(
        self, participant_id: uuid.UUID, *, owner_id: uuid.UUID | None = None
    ) -> Participant | None:
        statement = select(Participant).where(
            Participant.id == participant_id, col(Participant.deleted_at).is_(None)
        )
        if owner_id is not None:
            statement = statement.where(Participant.owner_id == owner_id)
        result = await self._session.execute(statement)
        return result.scalars().first()

    async def list_paginated(
        self, *, search: str | None, offset: int, limit: int, owner_id: uuid.UUID | None = None
    ) -> tuple[list[Participant], int]:
        base = select(Participant).where(col(Participant.deleted_at).is_(None))
        if owner_id is not None:
            base = base.where(Participant.owner_id == owner_id)
        if search:
            pattern = f"%{search.strip()}%"
            base = base.where(
                or_(
                    col(Participant.full_name).ilike(pattern),
                    col(Participant.phone).ilike(pattern),
                    col(Participant.document).ilike(pattern),
                    col(Participant.email).ilike(pattern),
                )
            )
        total = await self._session.execute(select(func.count()).select_from(base.subquery()))
        items = await self._session.execute(
            base.order_by(col(Participant.created_at).desc()).offset(offset).limit(limit)
        )
        return list(items.scalars().all()), int(total.scalar_one())

    async def get_by_phone(
        self, phone: str, *, owner_id: uuid.UUID | None = None
    ) -> Participant | None:
        statement = select(Participant).where(
            Participant.phone == phone, col(Participant.deleted_at).is_(None)
        )
        if owner_id is not None:
            statement = statement.where(Participant.owner_id == owner_id)
        result = await self._session.execute(statement)
        return result.scalars().first()

    async def phone_exists(
        self,
        phone: str,
        *,
        exclude_id: uuid.UUID | None = None,
        owner_id: uuid.UUID | None = None,
    ) -> bool:
        statement = select(Participant.id).where(
            Participant.phone == phone, col(Participant.deleted_at).is_(None)
        )
        if owner_id is not None:
            statement = statement.where(Participant.owner_id == owner_id)
        if exclude_id is not None:
            statement = statement.where(Participant.id != exclude_id)
        result = await self._session.execute(statement)
        return result.scalars().first() is not None

    async def save(self, participant: Participant) -> Participant:
        participant.updated_at = utcnow()
        self._session.add(participant)
        await self._session.flush()
        await self._session.refresh(participant)
        return participant

    async def soft_delete(self, participant: Participant) -> None:
        now = utcnow()
        participant.deleted_at = now
        participant.updated_at = now
        self._session.add(participant)
        await self._session.flush()
