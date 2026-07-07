from app.modules.tickets.exceptions import InvalidTicketQuantityError

MAX_TICKETS_PER_RAFFLE = 100_000


def ensure_valid_quantity(quantity: int) -> None:
    """Domain guard for bulk generation. Business rule, not an HTTP concern."""
    if quantity < 1:
        raise InvalidTicketQuantityError("Ticket quantity must be at least 1.")
    if quantity > MAX_TICKETS_PER_RAFFLE:
        raise InvalidTicketQuantityError(f"Ticket quantity cannot exceed {MAX_TICKETS_PER_RAFFLE}.")
