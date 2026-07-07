from fastapi import status

from app.core.exceptions import AppError, ConflictError


class EmailAlreadyRegisteredError(ConflictError):
    def __init__(self, message: str = "That email is already registered.") -> None:
        super().__init__(message)


class InvalidCredentialsError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, message: str = "Invalid email or password.") -> None:
        super().__init__(message)


class NotAuthenticatedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__(message)
