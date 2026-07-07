from app.core.exceptions import AppError, ConflictError, NotFoundError


class TicketNotFoundError(NotFoundError):
    def __init__(self, message: str = "Ticket not found.") -> None:
        super().__init__(message)


class TicketNotAvailableError(ConflictError):
    """Raised when reserving a ticket that is not AVAILABLE (already reserved,
    paid, etc.) — enforces 'cannot be reserved twice / sold twice'."""

    def __init__(self, message: str = "Ticket is not available for reservation.") -> None:
        super().__init__(message)


class TicketNotReservedError(ConflictError):
    """Raised when an action requires a RESERVED ticket (cancel / mark paid)."""

    def __init__(self, message: str = "Ticket is not currently reserved.") -> None:
        super().__init__(message)


class TicketImmutableError(ConflictError):
    """Raised when mutating a PAID or WINNER ticket — a paid ticket cannot be
    modified or deleted; it may only take part in the draw."""

    def __init__(self, message: str = "A paid or winning ticket cannot be modified.") -> None:
        super().__init__(message)


class TicketsAlreadyGeneratedError(ConflictError):
    def __init__(
        self, message: str = "Tickets have already been generated for this raffle."
    ) -> None:
        super().__init__(message)


class InvalidTicketQuantityError(AppError):
    """400 — invalid requested generation quantity."""


class ParticipantNotFoundForTicketError(NotFoundError):
    """Raised when assigning a participant that does not exist (surfaced from the
    DB foreign-key violation, so tickets stays decoupled from the participants module)."""

    def __init__(self, message: str = "Participant not found.") -> None:
        super().__init__(message)


class CollaboratorNotFoundForTicketError(NotFoundError):
    """Raised when crediting a collaborator that does not exist, is inactive, or
    does not belong to the ticket's raffle/owner."""

    def __init__(self, message: str = "Collaborator not found for this raffle.") -> None:
        super().__init__(message)
