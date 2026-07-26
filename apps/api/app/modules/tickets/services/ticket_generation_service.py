"""Bulk ticket generation as a pure domain operation.

Numbers are sequential integers starting_number..starting_number+quantity-1
(canonical stored value; starting_number is 0 or 1, fixed by the raffle at
creation). Zero-padded display labels (0001, 0002, ...) are a presentation
concern rendered at the edge from the raffle size, so nothing here formats
strings.
"""

import uuid
from datetime import datetime

from app.modules.tickets.models import Ticket, TicketStatus
from app.modules.tickets.validators import ensure_valid_quantity


class TicketGenerationService:
    @staticmethod
    def generate(
        raffle_id: uuid.UUID,
        quantity: int,
        *,
        now: datetime,
        owner_id: uuid.UUID | None = None,
        starting_number: int = 1,
    ) -> list[Ticket]:
        ensure_valid_quantity(quantity)
        return [
            Ticket(
                owner_id=owner_id,
                raffle_id=raffle_id,
                number=number,
                status=TicketStatus.AVAILABLE,
                created_at=now,
                updated_at=now,
            )
            for number in range(starting_number, starting_number + quantity)
        ]
