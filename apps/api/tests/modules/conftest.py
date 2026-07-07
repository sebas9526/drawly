"""Integration fixtures backed by an in-memory SQLite DB.

Overrides the app's get_session dependency so router -> use case -> repository
wiring runs end to end against a real (SQLite) database, without needing
Postgres or Docker. A single shared connection (StaticPool) keeps the in-memory
schema alive across sessions. SQLite foreign keys are enabled so the
tickets.participant_id / owner_id FKs behave like Postgres.

Auth: ``api_client`` registers and logs in a default user, so the httpx cookie
jar carries the session cookie on every request. Existing admin tests therefore
exercise the owner-scoped surface transparently (all their data belongs to that
one user). ``client_factory`` builds additional authenticated clients against
the *same* database for cross-user data-isolation tests.
"""

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from app.database.session import get_session
from app.main import app

# Import models so their tables are registered on SQLModel.metadata.
from app.modules.collaborators.models import Collaborator  # noqa: F401
from app.modules.participants.models import Participant  # noqa: F401
from app.modules.raffles.models import Raffle  # noqa: F401
from app.modules.tickets.models import Ticket  # noqa: F401
from app.modules.users.models import User  # noqa: F401

DEFAULT_EMAIL = "owner@drawly.test"
DEFAULT_PASSWORD = "password123"


async def register_user(
    client: AsyncClient,
    *,
    email: str = DEFAULT_EMAIL,
    full_name: str = "Default Owner",
    password: str = DEFAULT_PASSWORD,
) -> None:
    """Register a user; the response sets the session cookie on ``client``."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"full_name": full_name, "email": email, "password": password},
    )
    assert response.status_code == 201, response.text


def _new_engine() -> Any:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _enable_sqlite_fks(dbapi_connection: Any, _record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


@pytest.fixture
async def api_client() -> AsyncGenerator[AsyncClient]:
    engine = _new_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        async with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            await register_user(client)
            yield client
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.fixture
async def client_factory() -> AsyncGenerator[Callable[[str], Awaitable[AsyncClient]]]:
    """Yields a builder for additional authenticated clients on one shared DB.

    Each client owns its own cookie jar (a distinct authenticated user), so tests
    can assert that user A never sees user B's raffles/tickets/participants.
    """
    engine = _new_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        async with factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    created: list[AsyncClient] = []

    async def make(email: str) -> AsyncClient:
        client = AsyncClient(transport=transport, base_url="http://test")
        await client.__aenter__()
        created.append(client)
        await register_user(client, email=email, full_name=email)
        return client

    try:
        yield make
    finally:
        for client in created:
            await client.__aexit__(None, None, None)
        app.dependency_overrides.clear()
        await engine.dispose()
