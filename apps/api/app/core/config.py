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
    # No background job releases expired reservations yet (see tickets module).
    reservation_ttl_hours: int = 48

    database_url: str = "postgresql+asyncpg://drawly:drawly@localhost:5432/drawly"
    database_url_sync: str = "postgresql+psycopg://drawly:drawly@localhost:5432/drawly"

    backend_cors_origins: str = "http://localhost:3000"

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
