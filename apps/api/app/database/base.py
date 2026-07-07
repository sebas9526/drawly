"""Shared persistence base for every module's SQLModel tables.

Centralizes the audit contract mandated by docs/03-database/DATABASE_DESIGN.md
(UUID primary key + created_at / updated_at / deleted_at on every table), so no
module re-declares these columns. Soft delete is expressed through ``deleted_at``.
"""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

# Shared timezone-aware timestamp type. Typed ``Any`` because SQLModel's
# ``sa_type`` expects a type, while we intentionally pass a configured instance;
# a single TypeEngine instance is safe to share across columns (SQLAlchemy copies
# it per column). Reused by module models so no one re-specifies timezone=True.
TZ_DATETIME: Any = DateTime(timezone=True)


def utcnow() -> datetime:
    """Timezone-aware UTC now. Single source used across the domain."""
    return datetime.now(UTC)


def status_column_type(enum_cls: type[Enum]) -> Any:
    """SQLAlchemy type for an enum-backed status column.

    ``native_enum=False`` stores the value in a plain VARCHAR (matching
    docs/03-database/DATABASE_DESIGN.md — status is VARCHAR(20)) instead of a
    native PostgreSQL ENUM type, and ``values_callable`` persists the lowercase
    member *values* (e.g. "draft", "available") so the stored/wire form matches
    the @drawly/api-client contract. Returns a fresh instance per call.
    """
    return SAEnum(
        enum_cls,
        native_enum=False,
        length=20,
        values_callable=lambda enum: [member.value for member in enum],
    )


class UUIDAuditBase(SQLModel):
    """Mixin (non-table) providing UUID id and audit fields.

    Concrete tables inherit this and set ``table=True``. Timestamps are managed
    in Python (see ``utcnow``) rather than via DB defaults to keep behavior
    deterministic and unit-testable without a live database.
    """

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=utcnow, sa_type=TZ_DATETIME, nullable=False)
    updated_at: datetime = Field(default_factory=utcnow, sa_type=TZ_DATETIME, nullable=False)
    deleted_at: datetime | None = Field(default=None, sa_type=TZ_DATETIME, nullable=True)
