"""In-process rate limiting — no external cache/queue required.

A fixed-window counter keyed by ``(bucket name, client key)``, held in a single
process-wide dict. Correct for the current single-instance deployment (see
docker-compose.yml); a horizontally-scaled deployment would need a shared store
(e.g. Redis) instead, since each process would otherwise count independently.
"""

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from fastapi import Request

from app.core.config import get_settings
from app.core.exceptions import AppError


class RateLimitedError(AppError):
    status_code = 429

    def __init__(self) -> None:
        super().__init__("Too many requests. Please try again later.")


@dataclass
class _Window:
    started_at: float
    count: int


class FixedWindowRateLimiter:
    """One counter per ``(name, key)``; resets once ``window_seconds`` elapse.

    No locking: FastAPI's async dependencies run cooperatively on a single
    event loop and this method never awaits, so a request can't be preempted
    mid-mutation.
    """

    def __init__(self) -> None:
        self._windows: dict[tuple[str, str], _Window] = {}

    def hit(self, *, name: str, key: str, max_requests: int, window_seconds: int) -> None:
        now = time.monotonic()
        bucket = (name, key)
        window = self._windows.get(bucket)
        if window is None or now - window.started_at >= window_seconds:
            self._windows[bucket] = _Window(started_at=now, count=1)
            return
        window.count += 1
        if window.count > max_requests:
            raise RateLimitedError()


_limiter = FixedWindowRateLimiter()


def _client_key(request: Request) -> str:
    """Best-effort client identity. Trusts ``X-Forwarded-For`` (set by the
    reverse proxy in front of the API); an attacker controlling headers
    directly could spoof this, which is an accepted trade-off for a
    single-instance, in-memory limiter."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(
    *, name: str, max_requests: int, window_seconds: int
) -> Callable[[Request], Awaitable[None]]:
    """Dependency factory: raises ``RateLimitedError`` (429) past the
    threshold. A no-op while ``settings.rate_limit_enabled`` is False."""

    async def dependency(request: Request) -> None:
        settings = get_settings()
        if not settings.rate_limit_enabled:
            return
        _limiter.hit(
            name=name,
            key=_client_key(request),
            max_requests=max_requests,
            window_seconds=window_seconds,
        )

    return dependency
