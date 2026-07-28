from app.core.exceptions import NotFoundError


class PublicTicketNotFoundError(NotFoundError):
    """The requested ticket number does not exist in this raffle."""

    def __init__(self, message: str = "Ticket not found for this raffle.") -> None:
        super().__init__(message)


class PublicCollaboratorNotFoundError(NotFoundError):
    """The referral link's collaborator id doesn't exist, is inactive, or was
    deleted — treated the same (404) so an inactive collaborator's old link
    doesn't leak whether the id itself is real."""

    def __init__(self, message: str = "This referral link is not valid.") -> None:
        super().__init__(message)
