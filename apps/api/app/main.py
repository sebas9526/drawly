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

    yield

    if sweep_task is not None:
        await sweep_task.stop()
    await get_engine().dispose()


async def _run_reservation_sweep() -> None:
    released = await sweep_expired_reservations()
    if released:
        logger.info(
            "Reservation sweep released %d expired ticket(s): %s",
            len(released),
            [str(ticket.id) for ticket in released],
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
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    return app


app = create_app()
