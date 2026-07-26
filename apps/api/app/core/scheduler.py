"""Minimal in-process periodic task runner — no external cron/queue required.

A single asyncio task loops for the app's lifetime, invoking ``job`` every
``interval_seconds``. Started/stopped from the FastAPI lifespan (see
app/main.py). Used today for the reservation-expiry sweep (see
app/modules/tickets/jobs); the app's test suite never triggers a real ASGI
lifespan (tests call the app directly via ``httpx.ASGITransport``), so this
never runs during ``pytest``.
"""

import asyncio
import logging
from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Any

logger = logging.getLogger("app.scheduler")


class PeriodicTask:
    def __init__(
        self,
        *,
        name: str,
        interval_seconds: float,
        job: Callable[[], Awaitable[Any]],
    ) -> None:
        self._name = name
        self._interval_seconds = interval_seconds
        self._job = job
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._task is not None:
            return
        self._task = asyncio.create_task(self._run(), name=f"periodic:{self._name}")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        with suppress(asyncio.CancelledError):
            await self._task
        self._task = None

    async def _run(self) -> None:
        while True:
            await asyncio.sleep(self._interval_seconds)
            try:
                await self._job()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Periodic task %r failed", self._name)
