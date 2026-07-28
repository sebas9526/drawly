from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Drawly API"
    environment: str = "development"
    debug: bool = False

    api_v1_prefix: str = "/api/v1"

    # Hours a ticket reservation stays valid; persisted as expires_at on reserve.
    reservation_ttl_hours: int = 48
    # In-process sweep that releases expired reservations back to AVAILABLE (see
    # app/modules/tickets/dependencies.sweep_expired_reservations). No external
    # cron/queue required.
    reservation_sweep_enabled: bool = True
    reservation_sweep_interval_seconds: int = 60

    # In-process sweep that auto-publishes a DRAFT raffle once its optional
    # `publish_at` schedule arrives (see app/modules/raffles/dependencies.
    # sweep_scheduled_raffles). No external cron/queue required.
    raffle_publish_sweep_enabled: bool = True
    raffle_publish_sweep_interval_seconds: int = 60

    # In-process sweep that soft-deletes a CLOSED raffle (and its tickets) once
    # it's been closed for raffle_cleanup_grace_hours (see app/modules/raffles.
    # dependencies.sweep_closed_raffles). Runs infrequently since the grace
    # period is measured in hours, not seconds.
    raffle_cleanup_sweep_enabled: bool = True
    raffle_cleanup_sweep_interval_seconds: int = 60 * 60 * 12  # 12 hours
    raffle_cleanup_grace_hours: int = 24

    # --- Rate limiting (in-memory, single-process fixed window; see app/core/rate_limit.py) ---
    rate_limit_enabled: bool = True
    rate_limit_auth_max_requests: int = 5
    rate_limit_auth_window_seconds: int = 60
    rate_limit_public_max_requests: int = 60
    rate_limit_public_window_seconds: int = 60
    rate_limit_reserve_max_requests: int = 10
    rate_limit_reserve_window_seconds: int = 60

    database_url: str = "postgresql+asyncpg://drawly:drawly@localhost:5432/drawly"
    database_url_sync: str = "postgresql+psycopg://drawly:drawly@localhost:5432/drawly"

    backend_cors_origins: str = "http://localhost:3000"
    # Optional regex for origins that shouldn't require a BACKEND_CORS_ORIGINS
    # edit on every deploy — e.g. Vercel gives every deployment (production
    # included) its own unique URL in addition to the stable custom domain,
    # and preview deployments get their own per-branch URL too. Matched via
    # CORSMiddleware's allow_origin_regex, in addition to (not instead of)
    # the exact allow_origins list above. None disables it (no regex match).
    backend_cors_origin_regex: str | None = None

    # --- Auth (JWT in an httpOnly cookie) ---
    # Override JWT_SECRET in production via env. Dev default is fine locally.
    jwt_secret: str = "dev-insecure-change-me-in-production-please-32b"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24 * 7  # 7 days
    auth_cookie_name: str = "drawly_access"
    # Cookie flags. secure=False for local http; set true behind https.
    auth_cookie_secure: bool = False
    auth_cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
