import uuid

from app.modules.participants.exceptions import DuplicatePhoneError
from app.modules.participants.models import Participant
from app.modules.participants.schemas import ParticipantCreate, ParticipantUpdate


class ParticipantService:
    """Pure participant domain rules. No I/O — unit-testable without a DB."""

    @staticmethod
    def normalize_phone(phone: str) -> str:
        return phone.strip()

    @classmethod
    def build_participant(
        cls, data: ParticipantCreate, owner_id: uuid.UUID | None = None
    ) -> Participant:
        return Participant(
            owner_id=owner_id,
            full_name=data.full_name.strip(),
            phone=cls.normalize_phone(data.phone),
            email=data.email,
            document=data.document,
            address=data.address,
            city=data.city,
            notes=data.notes,
        )

    @staticmethod
    def ensure_phone_available(*, phone_taken: bool) -> None:
        if phone_taken:
            raise DuplicatePhoneError()

    @classmethod
    def apply_update(cls, participant: Participant, data: ParticipantUpdate) -> Participant:
        if data.full_name is not None:
            participant.full_name = data.full_name.strip()
        if data.phone is not None:
            participant.phone = cls.normalize_phone(data.phone)
        if data.email is not None:
            participant.email = data.email
        if data.document is not None:
            participant.document = data.document
        if data.address is not None:
            participant.address = data.address
        if data.city is not None:
            participant.city = data.city
        if data.notes is not None:
            participant.notes = data.notes
        return participant
