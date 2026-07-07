from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.database.session import get_session
from app.modules.users.exceptions import NotAuthenticatedError
from app.modules.users.models import User
from app.modules.users.repositories import UserRepository
from app.modules.users.use_cases import UserUseCases


def get_user_use_cases(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserUseCases:
    return UserUseCases(session=session, repository=UserRepository(session))


async def get_current_user(
    request: Request,
    use_cases: Annotated[UserUseCases, Depends(get_user_use_cases)],
) -> User:
    """Resolves the authenticated user from the httpOnly cookie (falling back to
    a Bearer header). Raises 401 when missing/invalid."""
    settings = get_settings()
    token = request.cookies.get(settings.auth_cookie_name)
    if token is None:
        authorization = request.headers.get("Authorization", "")
        if authorization.startswith("Bearer "):
            token = authorization[len("Bearer ") :]
    if not token:
        raise NotAuthenticatedError()

    user_id = decode_access_token(token)
    if user_id is None:
        raise NotAuthenticatedError()

    user = await use_cases.get(user_id)
    if user is None:
        raise NotAuthenticatedError()
    return user


UserUseCasesDep = Annotated[UserUseCases, Depends(get_user_use_cases)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
