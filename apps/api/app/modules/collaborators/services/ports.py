"""Ports the collaborators module depends on. Dependency Inversion keeps the
module decoupled from raffles/tickets internals: their use cases/repositories
satisfy these structurally, wired only in collaborators/dependencies.

Coupling stays one-directional (collaborators -> raffles, collaborators ->
tickets) and everything is testable via fakes.
"""

import uuid
from decimal import Decimal
from typing import Protocol


class CollaboratorRaffles(Protocol):
    """Raffle ownership + pricing lookup for the collaborators module."""

    async def owned_raffle_price(self, raffle_id: uuid.UUID, owner_id: uuid.UUID) -> Decimal | None:
        """Return the raffle's ticket price if it exists and belongs to
        ``owner_id``; otherwise ``None`` (used both to authorize and to price
        collaborator sales stats)."""
        ...


class CollaboratorTickets(Protocol):
    """Per-collaborator ticket aggregates for a raffle."""

    async def counts_by_collaborator(
        self, raffle_id: uuid.UUID
    ) -> dict[uuid.UUID, tuple[int, int]]:
        """Return ``{collaborator_id: (reserved_count, paid_count)}`` for the
        raffle. Collaborators with no tickets are simply absent."""
        ...
