"""Ports the tickets module depends on. Dependency Inversion keeps the tickets
domain decoupled from the collaborators module: the collaborators repository
satisfies this structurally, wired only in tickets/dependencies. No import cycle
— repositories never import dependencies."""

import uuid
from typing import Protocol


class TicketCollaborators(Protocol):
    """Validation that a collaborator may be credited on a ticket."""

    async def exists_in_raffle(
        self,
        collaborator_id: uuid.UUID,
        raffle_id: uuid.UUID,
        *,
        owner_id: uuid.UUID | None = None,
        active_only: bool = False,
    ) -> bool: ...
