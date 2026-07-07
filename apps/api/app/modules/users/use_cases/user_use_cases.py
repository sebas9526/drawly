import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.modules.users.models import User
from app.modules.users.repositories import UserRepository
from app.modules.users.schemas import LoginRequest, RegisterRequest
from app.modules.users.services import UserService


class UserUseCases:
    def __init__(
        self,
        session: AsyncSession,
        repository: UserRepository,
        service: UserService | None = None,
    ) -> None:
        self._session = session
        self._repository = repository
        self._service = service or UserService()

    async def register(self, data: RegisterRequest) -> User:
        if await self._repository.get_by_email(data.email) is not None:
            raise EmailAlreadyRegisteredError()
        user = self._service.build_user(data)
        created = await self._repository.add(user)
        await self._session.commit()
        return created

    async def authenticate(self, data: LoginRequest) -> User:
        user = await self._repository.get_by_email(data.email)
        # Verify even when the user is missing would be ideal (timing), but a
        # plain check is acceptable for the MVP.
        if user is None or not self._service.password_matches(user, data.password):
            raise InvalidCredentialsError()
        return user

    async def get(self, user_id: uuid.UUID) -> User | None:
        return await self._repository.get(user_id)
