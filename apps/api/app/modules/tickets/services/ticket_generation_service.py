"""Bulk ticket generation as a pure domain operation.

Numbers are sequential integers 1..quantity (canonical stored value). Zero-
padded display labels (0001, 0002, ...) are a presentation concern rendered at
the edge from the raffle size, so nothing here formats strings.
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
            for number in range(1, quantity + 1)
        ]
