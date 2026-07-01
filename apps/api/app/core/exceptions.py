import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.responses import ErrorResponse, FieldError

logger = logging.getLogger("app")


class AppError(Exception):
    """Base class for application errors that map to a standard error envelope."""

    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str, errors: list[FieldError] | None = None) -> None:
        self.message = message
        self.errors = errors or []
        super().__init__(message)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT


def _trace_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        body = ErrorResponse(message=exc.message, errors=exc.errors, trace_id=_trace_id(request))
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = [
            FieldError(field=".".join(str(loc) for loc in error["loc"]), message=error["msg"])
            for error in exc.errors()
        ]
        body = ErrorResponse(
            message="Validation failed.", errors=errors, trace_id=_trace_id(request)
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body.model_dump()
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", exc_info=exc)
        body = ErrorResponse(message="Internal server error.", trace_id=_trace_id(request))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body.model_dump()
        )
