from app.core.exceptions import ConflictError, NotFoundError


class RaffleNotFoundError(NotFoundError):
    def __init__(self, message: str = "Raffle not found.") -> None:
        super().__init__(message)


class RaffleNotEditableError(ConflictError):
    """A raffle can only be edited or have tickets generated while in draft."""

    def __init__(self, message: str = "Raffle can only be modified while in draft.") -> None:
        super().__init__(message)


class RaffleNotPublishableError(ConflictError):
    """A raffle can only be published from draft and once it has tickets."""

    def __init__(self, message: str = "Raffle cannot be published in its current state.") -> None:
        super().__init__(message)


class RaffleHasParticipantsError(ConflictError):
    """A raffle with tickets already assigned to participants cannot be
    deleted (docs/02-architecture/DOMAIN_MODEL.md)."""

    def __init__(
        self, message: str = "Raffle has tickets with participants and cannot be deleted."
    ) -> None:
        super().__init__(message)


class RaffleNotOpenForWinnerError(ConflictError):
    """A winner can only be registered on a published raffle — not a draft
    (nothing to draw from yet) and not an already-closed one (a winner was
    already confirmed)."""

    def __init__(self, message: str = "Raffle must be published to register a winner.") -> None:
        super().__init__(message)


class WinningTicketNotFoundError(NotFoundError):
    """The entered winning ticket number does not belong to this raffle."""

    def __init__(self, message: str = "No ticket with that number exists in this raffle.") -> None:
        super().__init__(message)
