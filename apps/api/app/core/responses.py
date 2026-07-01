from typing import Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")
ItemT = TypeVar("ItemT")


class SuccessResponse(BaseModel, Generic[DataT]):
    """Standard success envelope. See docs/04-api/RESPONSE_FORMAT.md."""

    success: bool = True
    message: str
    data: DataT


class FieldError(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    """Standard error envelope. See docs/04-api/ERROR_HANDLING.md."""

    success: bool = False
    message: str
    errors: list[FieldError] = []
    trace_id: str | None = None


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[ItemT]):
    success: bool = True
    data: list[ItemT]
    pagination: PaginationMeta
