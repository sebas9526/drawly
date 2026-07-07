"""Shared pagination helpers so every list endpoint builds the same envelope."""

from math import ceil

from app.core.responses import PaginationMeta


def offset_for(page: int, page_size: int) -> int:
    return (page - 1) * page_size


def build_pagination_meta(*, page: int, page_size: int, total: int) -> PaginationMeta:
    total_pages = ceil(total / page_size) if page_size and total else 0
    return PaginationMeta(page=page, page_size=page_size, total=total, total_pages=total_pages)
