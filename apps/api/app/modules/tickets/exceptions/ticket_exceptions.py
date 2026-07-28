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


class RaffleNotOpenForTicketsError(ConflictError):
    """A ticket can only be reserved, paid, or assigned a participant once its
    raffle is actually published — including while a raffle is waiting on a
    scheduled publish_at. Admin pre-arranging on an unpublished raffle is not
    allowed (see docs/02-architecture/DOMAIN_MODEL.md)."""

    def __init__(
        self, message: str = "This raffle is not published yet; tickets cannot be reserved."
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


class TicketNotPaidError(ConflictError):
    """Raised when confirming a winner for a ticket that isn't PAID — only a
    paid ticket is eligible to win (docs/02-architecture/DOMAIN_MODEL.md)."""

    def __init__(self, message: str = "Only a paid ticket can be marked as the winner.") -> None:
        super().__init__(message)
