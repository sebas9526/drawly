from app.core.exceptions import NotFoundError


class PublicTicketNotFoundError(NotFoundError):
    """The requested ticket number does not exist in this raffle."""

    def __init__(self, message: str = "Ticket not found for this raffle.") -> None:
        super().__init__(message)
