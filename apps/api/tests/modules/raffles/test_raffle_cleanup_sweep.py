"""Integration test for the closed-raffle cleanup sweep (RaffleUseCases.
cleanup_closed_raffles), backed by a real (SQLite) session — same reasoning
as test_raffle_publish_sweep.py: a system-wide background job with no HTTP
endpoint of its own (see app/modules/raffles/dependencies.sweep_closed_raffles
and the periodic scheduler wired in app/main.py).
"""

import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, select

from app.modules.raffles.models import Raffle, RaffleStatus
from app.modules.raffles.repositories import RaffleRepository
from app.modules.raffles.use_cases import RaffleUseCases
from app.modules.tickets.models import Ticket, TicketStatus
from app.modules.tickets.repositories import TicketRepository
from app.modules.tickets.use_cases import TicketUseCases

# cleanup_closed_raffles() compares against the real wall clock (utcnow()),
# not an injected value, so fixture data must be anchored to it.
NOW = datetime.now(UTC)
GRACE_HOURS = 24


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


async def _seed_closed_raffle(
    session: AsyncSession, *, closed_at: datetime | None, status: RaffleStatus = RaffleStatus.CLOSED
) -> tuple[Raffle, Ticket]:
    raffle = Raffle(
        title="Rifa",
        total_tickets=1,
        draw_date=NOW,
        public_slug=f"rifa-{uuid.uuid4()}",
        status=status,
        closed_at=closed_at,
    )
    session.add(raffle)
    await session.flush()
    ticket = Ticket(raffle_id=raffle.id, number=1, status=TicketStatus.WINNER)
    session.add(ticket)
    await session.flush()
    raffle.winner_ticket_id = ticket.id
    session.add(raffle)
    await session.flush()
    return raffle, ticket


async def test_sweep_deletes_a_raffle_closed_past_the_grace_period(session: AsyncSession) -> None:
    raffle, ticket = await _seed_closed_raffle(
        session, closed_at=NOW - timedelta(hours=GRACE_HOURS, minutes=1)
    )
    await session.commit()

    cleaned = await _use_cases(session).cleanup_closed_raffles(grace_hours=GRACE_HOURS)

    assert [r.id for r in cleaned] == [raffle.id]
    refreshed_raffle = await session.get(Raffle, raffle.id)
    refreshed_ticket = await session.get(Ticket, ticket.id)
    assert refreshed_raffle is not None and refreshed_raffle.deleted_at is not None
    assert refreshed_ticket is not None and refreshed_ticket.deleted_at is not None


async def test_sweep_ignores_a_raffle_still_inside_the_grace_period(
    session: AsyncSession,
) -> None:
    await _seed_closed_raffle(session, closed_at=NOW - timedelta(hours=1))
    await session.commit()

    cleaned = await _use_cases(session).cleanup_closed_raffles(grace_hours=GRACE_HOURS)

    assert cleaned == []


async def test_sweep_ignores_a_published_raffle_with_an_unresolved_winner_attempt(
    session: AsyncSession,
) -> None:
    """closed_at stays None for an invalid (unpaid) winner attempt — the
    sweep must never touch a raffle that's still open."""
    await _seed_closed_raffle(session, closed_at=None, status=RaffleStatus.PUBLISHED)
    await session.commit()

    cleaned = await _use_cases(session).cleanup_closed_raffles(grace_hours=GRACE_HOURS)

    assert cleaned == []


async def test_sweep_is_idempotent_on_retry(session: AsyncSession) -> None:
    """A second run after the tickets/raffle are already soft-deleted must be
    a safe no-op (list_closed_past_cutoff excludes already-deleted rows)."""
    raffle, _ = await _seed_closed_raffle(
        session, closed_at=NOW - timedelta(hours=GRACE_HOURS, minutes=1)
    )
    await session.commit()
    first = await _use_cases(session).cleanup_closed_raffles(grace_hours=GRACE_HOURS)
    assert len(first) == 1

    second = await _use_cases(session).cleanup_closed_raffles(grace_hours=GRACE_HOURS)
    assert second == []

    remaining = await session.execute(select(Raffle).where(Raffle.id == raffle.id))
    assert remaining.scalars().first() is not None  # soft-deleted, not gone
