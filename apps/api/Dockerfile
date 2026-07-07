# syntax=docker/dockerfile:1
# Build context must be apps/api:
#   docker build -t drawly-api ./apps/api

FROM python:3.12-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1
WORKDIR /app

# ---- Dependencies layer (cached unless pyproject.toml/uv.lock change) ----
# Non-frozen so a newly added dependency resolves during build without
# regenerating uv.lock on the host first.
FROM base AS deps
COPY pyproject.toml uv.lock ./
RUN uv sync --no-install-project

# ---- Development image: source is bind-mounted by docker-compose ----
FROM deps AS dev
COPY . .
RUN uv sync
EXPOSE 8000
# Entrypoint runs `alembic upgrade head` before the CMD, so the schema is
# provisioned automatically on `docker compose up`.
ENTRYPOINT ["/bin/sh", "/app/docker-entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

# ---- Production image ----
FROM deps AS production
COPY . .
RUN uv sync --no-dev
EXPOSE 8000
ENTRYPOINT ["/bin/sh", "/app/docker-entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
