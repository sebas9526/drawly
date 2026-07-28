"""Regression test: updating a collaborator used to re-validate ownership of
*every* raffle in raffle_ids on every edit, including ones that were already
linked and untouched. That made a collaborator permanently un-editable the
moment it had a link to a raffle that can't pass today's ownership check —
e.g. a legacy raffle with owner_id=None from before auth existed (a real
scenario found in production). Editing must only validate newly-added ids.

Uses a raw session (like test_raffle_publish_sweep.py) since there's no HTTP
path to create an owner_id=None raffle — the API always stamps the
authenticated caller's id.
"""

import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.modules.collaborators.dependencies.collaborator_dependencies import _build
from app.modules.collaborators.models import Collaborator
from app.modules.collaborators.repositories import CollaboratorRepository
from app.modules.collaborators.schemas import CollaboratorUpdate
from app.modules.raffles.models import Raffle

NOW = datetime.now(UTC)


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine(
        "sqlite+aiosqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as db_session:
        yield db_session
    await engine.dispose()


async def test_update_does_not_reject_an_already_linked_legacy_raffle(
    session: AsyncSession,
) -> None:
    owner_id = uuid.uuid4()
    # Legacy raffle: no owner (created before auth), so it can never pass
    # the ownership check today.
    legacy_raffle = Raffle(
        title="Rifa vieja",
        total_tickets=5,
        draw_date=NOW,
        public_slug=f"rifa-{uuid.uuid4()}",
        owner_id=None,
    )
    session.add(legacy_raffle)
    await session.flush()

    collaborator = Collaborator(owner_id=owner_id, name="Ana")
    session.add(collaborator)
    await session.flush()
    await CollaboratorRepository(session).set_raffles(collaborator.id, [legacy_raffle.id])
    await session.commit()

    use_cases = _build(session, owner_id)

    # Editing an unrelated field, resubmitting the same (already-linked,
    # unowned) raffle_ids, must succeed rather than 404.
    updated = await use_cases.update(
        collaborator.id,
        CollaboratorUpdate(name="Ana María", raffle_ids=[legacy_raffle.id]),
    )
    assert updated.name == "Ana María"
    assert updated.raffle_ids == [legacy_raffle.id]
