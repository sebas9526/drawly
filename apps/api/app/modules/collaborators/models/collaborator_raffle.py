import uuid

from sqlalchemy import Index
from sqlmodel import Field

from app.database.base import UUIDAuditBase


class CollaboratorRaffle(UUIDAuditBase, table=True):
    """Join row: a collaborator sells for a raffle. Many-to-many — the same
    collaborator can be linked to several raffles, and a raffle can have many
    collaborators (docs/02-architecture/DOMAIN_MODEL.md).

    Uniqueness of the (collaborator_id, raffle_id) pair among non-deleted rows
    is enforced at the application layer only (CollaboratorRepository.
    set_raffles), the same pattern as Raffle.public_slug — a DB-level unique
    constraint would outlive a soft-deleted link and permanently block
    re-linking the same pair later.
    """

    __tablename__ = "collaborator_raffles"
    __table_args__ = (Index("ix_collaborator_raffles_pair", "collaborator_id", "raffle_id"),)

    collaborator_id: uuid.UUID = Field(foreign_key="collaborators.id", index=True)
    # ON DELETE CASCADE: a raffle hard-delete (RaffleUseCases.delete) should
    # take its collaborator links with it — this is a pure join table, so the
    # DB handles that cleanup itself rather than the raffles module needing a
    # new cross-module port just to clear it (see migration 0012).
    raffle_id: uuid.UUID = Field(foreign_key="raffles.id", index=True, ondelete="CASCADE")
