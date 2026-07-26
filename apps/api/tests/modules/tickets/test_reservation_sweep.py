"""Integration test for the reservation-expiry sweep (TicketUseCases.
release_expired_reservations), backed by a real (SQLite) session — the sweep
is a system-wide background job with no HTTP endpoint of its own (see
app/modules/tickets/dependencies.sweep_expired_reservations and the periodic
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

from app.modules.raffles.models import Raffle
from app.modules.tickets.models import Ticket, TicketStatus
from app.modules.tickets.repositories import TicketRepository
from app.modules.tickets.use_cases import TicketUseCases

# release_expired_reservations() compares against the real wall clock
# (utcnow()), not an injected value, so fixture data must be anchored to it —
# a fixed historical timestamp could accidentally already be "expired".
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


async def _seed_raffle(db_session: AsyncSession) -> Raffle:
    raffle = Raffle(
        title="Rifa",
        total_tickets=2,
        draw_date=NOW,
        public_slug=f"rifa-{uuid.uuid4()}",
    )
    db_session.add(raffle)
    await db_session.flush()
    return raffle


async def _seed_reserved_ticket(
    db_session: AsyncSession, raffle: Raffle, *, number: int, expires_at: datetime | None
) -> Ticket:
    ticket = Ticket(
        raffle_id=raffle.id,
        number=number,
        status=TicketStatus.RESERVED,
        participant_id=uuid.uuid4(),
        collaborator_id=uuid.uuid4(),
        reserved_at=NOW - timedelta(hours=1),
        expires_at=expires_at,
    )
    db_session.add(ticket)
    await db_session.flush()
    return ticket


async def test_sweep_releases_only_expired_reservations(session: AsyncSession) -> None:
    raffle = await _seed_raffle(session)
    expired = await _seed_reserved_ticket(
        session, raffle, number=1, expires_at=NOW - timedelta(minutes=1)
    )
    still_valid = await _seed_reserved_ticket(
        session, raffle, number=2, expires_at=NOW + timedelta(hours=1)
    )
    await session.commit()

    use_cases = TicketUseCases(session=session, repository=TicketRepository(session))
    released = await use_cases.release_expired_reservations()

    assert [ticket.id for ticket in released] == [expired.id]
    assert released[0].status is TicketStatus.AVAILABLE
    assert released[0].participant_id is None
    assert released[0].collaborator_id is None
    assert released[0].reserved_at is None
    assert released[0].expires_at is None

    refreshed_valid = await TicketRepository(session).get(still_valid.id)
    assert refreshed_valid is not None
    assert refreshed_valid.status is TicketStatus.RESERVED


async def test_sweep_is_a_noop_without_expired_reservations(session: AsyncSession) -> None:
    raffle = await _seed_raffle(session)
    await _seed_reserved_ticket(session, raffle, number=1, expires_at=NOW + timedelta(hours=1))
    await session.commit()

    use_cases = TicketUseCases(session=session, repository=TicketRepository(session))
    released = await use_cases.release_expired_reservations()

    assert released == []
