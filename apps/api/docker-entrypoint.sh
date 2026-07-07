#!/bin/sh
# Applies database migrations, then hands off to the container's CMD (uvicorn).
# Keeps the API image self-provisioning: `docker compose up` creates the schema
# with no manual `alembic upgrade head` step.
set -e

echo "[entrypoint] Applying database migrations..."
attempt=0
until uv run alembic upgrade head; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 15 ]; then
    echo "[entrypoint] Migrations failed after $attempt attempts — aborting."
    exit 1
  fi
  echo "[entrypoint] Database not ready yet, retrying in 2s ($attempt/15)..."
  sleep 2
done

echo "[entrypoint] Migrations applied. Starting API..."
exec "$@"
