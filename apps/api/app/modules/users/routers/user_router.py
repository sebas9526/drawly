import uuid

from fastapi import APIRouter, Response, status

from app.core.config import get_settings
from app.core.responses import SuccessResponse
from app.core.security import create_access_token
from app.modules.users.dependencies import CurrentUserDep, UserUseCasesDep
from app.modules.users.schemas import LoginRequest, RegisterRequest, UserRead

router = APIRouter()


def _set_auth_cookie(response: Response, user_id: uuid.UUID) -> None:
    settings = get_settings()
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=create_access_token(user_id),
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite=settings.auth_cookie_samesite,
        max_age=settings.jwt_expires_minutes * 60,
        path="/",
    )


@router.post(
    "/register", response_model=SuccessResponse[UserRead], status_code=status.HTTP_201_CREATED
)
async def register(
    payload: RegisterRequest, response: Response, use_cases: UserUseCasesDep
) -> SuccessResponse[UserRead]:
    user = await use_cases.register(payload)
    _set_auth_cookie(response, user.id)
    return SuccessResponse(message="Account created.", data=UserRead.from_entity(user))


@router.post("/login", response_model=SuccessResponse[UserRead])
async def login(
    payload: LoginRequest, response: Response, use_cases: UserUseCasesDep
) -> SuccessResponse[UserRead]:
    user = await use_cases.authenticate(payload)
    _set_auth_cookie(response, user.id)
    return SuccessResponse(message="Signed in.", data=UserRead.from_entity(user))


@router.post("/logout", response_model=SuccessResponse[dict[str, bool]])
async def logout(response: Response) -> SuccessResponse[dict[str, bool]]:
    settings = get_settings()
    response.delete_cookie(settings.auth_cookie_name, path="/")
    return SuccessResponse(message="Signed out.", data={"ok": True})


@router.get("/me", response_model=SuccessResponse[UserRead])
async def me(current_user: CurrentUserDep) -> SuccessResponse[UserRead]:
    return SuccessResponse(message="Current user.", data=UserRead.from_entity(current_user))
