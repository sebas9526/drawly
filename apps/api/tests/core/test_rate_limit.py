"""Pure unit tests for the in-memory fixed-window rate limiter — no app, no
database. Exercises the counting logic directly (see also
tests/modules/test_public_flow_api.py and test_auth_api.py, which confirm
rate limiting stays off by default in the test suite).

The FastAPI route wiring itself (``_auth_rate_limit`` / ``_public_rate_limit``
in the users/public routers) is not exercised end-to-end here: those
dependencies capture ``max_requests``/``window_seconds`` from ``get_settings()``
at *router import time* (a process-wide ``lru_cache``), so a full-app,
settings-flipping integration test would need to fight that cache rather than
verify anything new — the ``rate_limit()`` factory below is the actual unit
under test either way. End-to-end 429 behavior is verified manually against a
running server (see the sprint report's verification checklist).
"""

from dataclasses import dataclass
from typing import cast

import pytest
from fastapi import Request

from app.core.rate_limit import FixedWindowRateLimiter, RateLimitedError, rate_limit


def test_allows_requests_up_to_the_limit() -> None:
    limiter = FixedWindowRateLimiter()
    for _ in range(5):
        limiter.hit(name="auth", key="1.2.3.4", max_requests=5, window_seconds=60)


def test_rejects_the_request_past_the_limit() -> None:
    limiter = FixedWindowRateLimiter()
    for _ in range(5):
        limiter.hit(name="auth", key="1.2.3.4", max_requests=5, window_seconds=60)
    with pytest.raises(RateLimitedError):
        limiter.hit(name="auth", key="1.2.3.4", max_requests=5, window_seconds=60)


def test_buckets_are_isolated_by_name_and_key() -> None:
    limiter = FixedWindowRateLimiter()
    for _ in range(5):
        limiter.hit(name="auth", key="1.2.3.4", max_requests=5, window_seconds=60)

    # Different client: unaffected by the first client's exhausted window.
    limiter.hit(name="auth", key="5.6.7.8", max_requests=5, window_seconds=60)
    # Different bucket name for the same client: also unaffected.
    limiter.hit(name="public", key="1.2.3.4", max_requests=5, window_seconds=60)


def test_window_resets_after_it_elapses() -> None:
    limiter = FixedWindowRateLimiter()
    limiter.hit(name="auth", key="1.2.3.4", max_requests=1, window_seconds=0)
    # window_seconds=0 means the very next call is already past the window.
    limiter.hit(name="auth", key="1.2.3.4", max_requests=1, window_seconds=0)


@dataclass
class _FakeClient:
    host: str


class _FakeRequest:
    """Stand-in for ``fastapi.Request`` — the dependency only reads
    ``headers``/``client.host``, so a full Starlette Request isn't needed."""

    def __init__(self, *, ip: str = "9.9.9.9", forwarded_for: str | None = None) -> None:
        self.client = _FakeClient(host=ip)
        self.headers = {"x-forwarded-for": forwarded_for} if forwarded_for else {}


async def test_rate_limit_dependency_raises_past_the_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The test suite runs with RATE_LIMIT_ENABLED=false (see tests/conftest.py)
    so this patches the flag on just for this test, verifying the dependency's
    own enabled/disabled branch and its call into the limiter."""
    import app.core.rate_limit as rate_limit_module

    class _FakeSettings:
        rate_limit_enabled = True

    monkeypatch.setattr(rate_limit_module, "get_settings", lambda: _FakeSettings())
    monkeypatch.setattr(rate_limit_module, "_limiter", FixedWindowRateLimiter())

    dependency = rate_limit(name="test-bucket", max_requests=2, window_seconds=60)
    request = cast(Request, _FakeRequest(ip="10.0.0.1"))

    await dependency(request)
    await dependency(request)
    with pytest.raises(RateLimitedError):
        await dependency(request)


async def test_rate_limit_dependency_is_a_noop_when_disabled() -> None:
    """Confirms the default test environment (RATE_LIMIT_ENABLED=false) never
    throttles — the exact property the rest of the test suite relies on."""
    dependency = rate_limit(name="test-bucket-disabled", max_requests=1, window_seconds=60)
    request = cast(Request, _FakeRequest(ip="10.0.0.2"))

    for _ in range(10):
        await dependency(request)
