"""Pure domain / schema unit tests for participants — no DB involved."""

import pytest

from app.modules.participants.exceptions import DuplicatePhoneError
from app.modules.participants.models import Participant
from app.modules.participants.schemas import ParticipantCreate, ParticipantUpdate
from app.modules.participants.services import ParticipantService


def test_build_participant_trims_name_and_phone() -> None:
    participant = ParticipantService.build_participant(
        ParticipantCreate(full_name="  Ana Díaz  ", phone="  300 111 ")
    )
    assert participant.full_name == "Ana Díaz"
    assert participant.phone == "300 111"


def test_ensure_phone_available_raises_when_taken() -> None:
    with pytest.raises(DuplicatePhoneError):
        ParticipantService.ensure_phone_available(phone_taken=True)


def test_ensure_phone_available_passes_when_free() -> None:
    ParticipantService.ensure_phone_available(phone_taken=False)


def test_apply_update_only_touches_provided_fields() -> None:
    participant = Participant(full_name="Ana", phone="300")
    ParticipantService.apply_update(participant, ParticipantUpdate(city="Bogotá"))
    assert participant.city == "Bogotá"
    assert participant.full_name == "Ana"
    assert participant.phone == "300"


def test_create_schema_rejects_invalid_email() -> None:
    with pytest.raises(ValueError):
        ParticipantCreate(full_name="Ana", phone="300", email="not-an-email")


def test_create_schema_accepts_valid_email() -> None:
    participant = ParticipantCreate(full_name="Ana", phone="300", email="ana@example.com")
    assert participant.email == "ana@example.com"


def test_create_schema_blank_email_becomes_none() -> None:
    participant = ParticipantCreate(full_name="Ana", phone="300", email="")
    assert participant.email is None
