import uuid

from sqlmodel import Field

from app.database.base import UUIDAuditBase


class Collaborator(UUIDAuditBase, table=True):
    """A sales collaborator, reusable across any number of raffles (see
    CollaboratorRaffle for the link table — a collaborator sells for zero or
    more raffles, a raffle has many collaborators).

    When a ticket is reserved/paid it may record which collaborator made the
    sale (see ``tickets.collaborator_id``).

    Multi-tenancy: ``owner_id`` is denormalized from the raffle owner so every
    admin query can be scoped without a join (same pattern as tickets).

    Growth path (docs/02-architecture/DOMAIN_MODEL.md): ``user_id`` is reserved,
    nullable, and unset for now. Later a collaborator can be linked to a platform
    ``User`` so they can log in and see only their own sales — no schema rewrite,
    just populate the column.
    """

    __tablename__ = "collaborators"

    # Owner (the authenticated organizer). Nullable for rows created before auth.
    owner_id: uuid.UUID | None = Field(default=None, foreign_key="users.id", index=True)
    # Reserved for the future "collaborator becomes a login user" flow.
    user_id: uuid.UUID | None = Field(default=None, foreign_key="users.id", index=True)

    name: str = Field(max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, index=True, max_length=150)
    # Display color (hex, e.g. "#4F46E5") used to tag the collaborator in the UI.
    color: str = Field(default="#4F46E5", max_length=9)
    notes: str | None = Field(default=None)
    is_active: bool = Field(default=True, index=True)
