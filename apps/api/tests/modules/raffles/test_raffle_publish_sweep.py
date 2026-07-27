"""Integration test for the raffle-publish sweep (RaffleUseCases.
publish_scheduled_raffles), backed by a real (SQLite) session — same
reasoning as tests/modules/tickets/test_reservation_sweep.py: this is a
system-wide background job with no HTTP endpoint of its own (see
app/modules/raffles/dependencies.sweep_scheduled_raffles and the periodic
scheduler wired in app/main.py), so it's exercised here at the use-case layer
directly rather than through the API.
"""

import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.modules.raffles.models import Raffle, RaffleStatus
from app.modules.raffles.repositories import RaffleRepository
from app.modules.raffles.use_cases import RaffleUseCases
from app.modules.tickets.models import Ticket, TicketStatus
from app.modules.tickets.repositories import TicketRepository
from app.modules.tickets.use_cases import TicketUseCases

# publish_scheduled_raffles() compares against the real wall clock (utcnow()),
# not an injected value, so fixture data must be anchored to it — a fixed
# historical timestamp could accidentally already be "due".
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


def _use_cases(session: AsyncSession) -> RaffleUseCases:
    tickets = TicketUseCases(session=session, repository=TicketRepository(session))
    return RaffleUseCases(session=session, repository=RaffleRepository(session), tickets=tickets)


async def _seed_raffle(
    session: AsyncSession, *, publish_at: datetime | None, with_tickets: bool
) -> Raffle:
    raffle = Raffle(
        title="Rifa",
        total_tickets=2,
        draw_date=NOW,
        public_slug=f"rifa-{uuid.uuid4()}",
        publish_at=publish_at,
    )
    session.add(raffle)
    await session.flush()
    if with_tickets:
        for number in (1, 2):
            session.add(Ticket(raffle_id=raffle.id, number=number, status=TicketStatus.AVAILABLE))
        await session.flush()
    return raffle


async def test_sweep_publishes_a_scheduled_raffle_with_tickets(session: AsyncSession) -> None:
    raffle = await _seed_raffle(session, publish_at=NOW - timedelta(minutes=1), with_tickets=True)
    await session.commit()

    published = await _use_cases(session).publish_scheduled_raffles()

    assert [r.id for r in published] == [raffle.id]
    assert published[0].status is RaffleStatus.PUBLISHED


async def test_sweep_skips_a_scheduled_raffle_without_tickets_yet(session: AsyncSession) -> None:
    """The schedule firing before tickets exist must not be dropped silently
    — it should stay DRAFT and be retried on the next tick."""
    raffle = await _seed_raffle(session, publish_at=NOW - timedelta(minutes=1), with_tickets=False)
    await session.commit()

    published = await _use_cases(session).publish_scheduled_raffles()

    assert published == []
    refreshed = await RaffleRepository(session).get(raffle.id)
    assert refreshed is not None
    assert refreshed.status is RaffleStatus.DRAFT


async def test_sweep_ignores_a_raffle_scheduled_in_the_future(session: AsyncSession) -> None:
    await _seed_raffle(session, publish_at=NOW + timedelta(hours=1), with_tickets=True)
    await session.commit()

    published = await _use_cases(session).publish_scheduled_raffles()

    assert published == []


async def test_sweep_ignores_a_raffle_with_no_schedule(session: AsyncSession) -> None:
    """publish_at=None is the default (today's fully-manual behavior) — the
    sweep must never touch these."""
    await _seed_raffle(session, publish_at=None, with_tickets=True)
    await session.commit()

    published = await _use_cases(session).publish_scheduled_raffles()

    assert published == []
