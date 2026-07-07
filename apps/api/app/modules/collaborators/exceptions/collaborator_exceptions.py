from app.core.exceptions import NotFoundError


class CollaboratorNotFoundError(NotFoundError):
    def __init__(self, message: str = "Collaborator not found.") -> None:
        super().__init__(message)


class RaffleNotFoundForCollaboratorError(NotFoundError):
    """The target raffle does not exist or does not belong to the current user.

    Surfaced as 404 (not 403) so a user cannot probe which raffle ids exist
    outside their account.
    """

    def __init__(self, message: str = "Raffle not found.") -> None:
        super().__init__(message)
