import uuid
from typing import Protocol


class TicketProvisioning(Protocol):
    """Port the raffle aggregate uses to provision its tickets.

    Dependency Inversion: the raffles domain depends on this abstraction, not on
    the tickets module. The tickets module's use case satisfies it structurally,
    and the dependencies layer performs the concrete wiring. Keeps module
    coupling one-directional (raffles -> tickets) and testable via fakes.
    """

    async def generate_for_raffle(
        self, raffle_id: uuid.UUID, quantity: int, owner_id: uuid.UUID | None = None
    ) -> int: ...

    async def count_for_raffle(self, raffle_id: uuid.UUID) -> int: ...
