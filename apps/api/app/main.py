import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.v1.router import api_router as api_v1_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.scheduler import PeriodicTask
from app.database.session import get_engine
from app.middleware.request_id import RequestIDMiddleware
from app.modules.raffles.dependencies import sweep_closed_raffles, sweep_scheduled_raffles
from app.modules.tickets.dependencies import sweep_expired_reservations

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()
    sweep_task: PeriodicTask | None = None
    if settings.reservation_sweep_enabled:
        sweep_task = PeriodicTask(
            name="reservation-sweep",
            interval_seconds=settings.reservation_sweep_interval_seconds,
            job=_run_reservation_sweep,
        )
        sweep_task.start()

    publish_sweep_task: PeriodicTask | None = None
    if settings.raffle_publish_sweep_enabled:
        publish_sweep_task = PeriodicTask(
            name="raffle-publish-sweep",
            interval_seconds=settings.raffle_publish_sweep_interval_seconds,
            job=_run_raffle_publish_sweep,
        )
        publish_sweep_task.start()

    cleanup_sweep_task: PeriodicTask | None = None
    if settings.raffle_cleanup_sweep_enabled:
        cleanup_sweep_task = PeriodicTask(
            name="raffle-cleanup-sweep",
            interval_seconds=settings.raffle_cleanup_sweep_interval_seconds,
            job=_run_raffle_cleanup_sweep,
        )
        cleanup_sweep_task.start()

    yield

    if sweep_task is not None:
        await sweep_task.stop()
    if publish_sweep_task is not None:
        await publish_sweep_task.stop()
    if cleanup_sweep_task is not None:
        await cleanup_sweep_task.stop()
    await get_engine().dispose()


async def _run_reservation_sweep() -> None:
    released = await sweep_expired_reservations()
    if released:
        logger.info(
            "Reservation sweep released %d expired ticket(s): %s",
            len(released),
            [str(ticket.id) for ticket in released],
        )


async def _run_raffle_publish_sweep() -> None:
    published = await sweep_scheduled_raffles()
    if published:
        logger.info(
            "Raffle publish sweep activated %d scheduled raffle(s): %s",
            len(published),
            [str(raffle.id) for raffle in published],
        )


async def _run_raffle_cleanup_sweep() -> None:
    cleaned = await sweep_closed_raffles()
    if cleaned:
        logger.info(
            "Raffle cleanup sweep deleted %d concluded raffle(s): %s",
            len(cleaned),
            [str(raffle.id) for raffle in cleaned],
        )


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=settings.backend_cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
