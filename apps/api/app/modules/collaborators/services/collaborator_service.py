import uuid

from app.modules.collaborators.models import Collaborator
from app.modules.collaborators.schemas import CollaboratorCreate, CollaboratorUpdate


class CollaboratorService:
    """Pure collaborator domain rules. No I/O — unit-testable without a DB."""

    @staticmethod
    def build_collaborator(data: CollaboratorCreate, *, owner_id: uuid.UUID | None) -> Collaborator:
        return Collaborator(
            owner_id=owner_id,
            name=data.name.strip(),
            phone=data.phone,
            email=data.email,
            color=data.color,
            notes=data.notes,
            is_active=data.is_active,
        )

    @staticmethod
    def apply_update(collaborator: Collaborator, data: CollaboratorUpdate) -> Collaborator:
        if data.name is not None:
            collaborator.name = data.name.strip()
        if data.phone is not None:
            collaborator.phone = data.phone
        if data.email is not None:
            collaborator.email = data.email
        if data.color is not None:
            collaborator.color = data.color
        if data.notes is not None:
            collaborator.notes = data.notes
        if data.is_active is not None:
            collaborator.is_active = data.is_active
        return collaborator
