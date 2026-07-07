import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from app.modules.users.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def get(self, user_id: uuid.UUID) -> User | None:
        statement = select(User).where(User.id == user_id, col(User.deleted_at).is_(None))
        result = await self._session.execute(statement)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email.lower(), col(User.deleted_at).is_(None))
        result = await self._session.execute(statement)
        return result.scalars().first()
