from app.core.exceptions import ConflictError, NotFoundError


class ParticipantNotFoundError(NotFoundError):
    def __init__(self, message: str = "Participant not found.") -> None:
        super().__init__(message)


class DuplicatePhoneError(ConflictError):
    """Phone uniqueness is enforced at the service layer among active
    (non-deleted) participants (DATABASE_DESIGN keeps the column non-unique)."""

    def __init__(self, message: str = "A participant with this phone already exists.") -> None:
        super().__init__(message)


class ParticipantHasTicketsError(ConflictError):
    """A participant with assigned tickets cannot be deleted; unassign/cancel
    those tickets first so no ticket references a deleted participant."""

    def __init__(
        self, message: str = "Participant has tickets assigned and cannot be deleted."
    ) -> None:
        super().__init__(message)
