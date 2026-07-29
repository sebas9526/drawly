import uuid
from typing import NamedTuple, Protocol


class TicketWinnerCandidate(NamedTuple):
    """What the raffle aggregate needs to decide whether an entered ticket
    number is a valid winner, without importing the tickets module's Ticket
    model."""

    ticket_id: uuid.UUID
    participant_id: uuid.UUID | None
    is_paid: bool


class TicketProvisioning(Protocol):
    """Port the raffle aggregate uses to provision its tickets and register a
    winner.

    Dependency Inversion: the raffles domain depends on this abstraction, not on
    the tickets module. The tickets module's use case satisfies it structurally,
    and the dependencies layer performs the concrete wiring. Keeps module
    coupling one-directional (raffles -> tickets) and testable via fakes.
    """

    async def generate_for_raffle(
        self,
        raffle_id: uuid.UUID,
        quantity: int,
        owner_id: uuid.UUID | None = None,
        starting_number: int = 1,
    ) -> int: ...

    async def count_for_raffle(self, raffle_id: uuid.UUID) -> int: ...

    async def count_with_participant_for_raffle(self, raffle_id: uuid.UUID) -> int: ...

    async def find_winner_candidate(
        self, raffle_id: uuid.UUID, number: int
    ) -> TicketWinnerCandidate | None: ...

    async def confirm_winner(self, ticket_id: uuid.UUID) -> None: ...

    async def hard_delete_all_for_raffle(self, raffle_id: uuid.UUID) -> int: ...
