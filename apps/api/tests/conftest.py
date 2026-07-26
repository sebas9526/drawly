import os

# Must be set before `app.main` (and therefore `app.core.config.get_settings`,
# which is @lru_cache'd) is imported for the first time. Rate limiting is a
# production hardening feature (see app/core/rate_limit.py); the test suite
# hits /auth/register and /public/*/reserve far more than any real client
# would in the same window, so it stays off unless a test opts in explicitly.
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

from collections.abc import AsyncGenerator  # noqa: E402

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
