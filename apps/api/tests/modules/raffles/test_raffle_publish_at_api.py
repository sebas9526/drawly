"""API-level contract test for the optional `publish_at` field: create,
read-back, and update, through the real HTTP layer (SQLite-backed). The
sweep's own behavior is covered by test_raffle_publish_sweep.py at the
use-case layer — this only checks the JSON contract.
"""

from datetime import UTC, datetime, timedelta

from httpx import AsyncClient

API = "/api/v1"


async def test_raffle_create_without_publish_at_defaults_to_null(
    api_client: AsyncClient,
) -> None:
    response = await api_client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa manual",
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": 10,
            "draw_date": "2026-09-01T19:00:00+00:00",
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["data"]["publish_at"] is None


async def test_raffle_create_with_publish_at_round_trips(api_client: AsyncClient) -> None:
    response = await api_client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa programada",
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": 10,
            "draw_date": "2026-09-01T19:00:00+00:00",
            "publish_at": "2026-08-01T00:00:00+00:00",
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    # SQLite (this test's engine) doesn't preserve tz-awareness on round-trip
    # the way Postgres does, so the serialized suffix can be "Z" or bare —
    # the value itself is what matters here, not that formatting quirk.
    assert data["publish_at"].startswith("2026-08-01T00:00:00")
    assert data["status"] == "draft"


async def test_raffle_publish_at_can_be_changed_via_update(api_client: AsyncClient) -> None:
    created = await api_client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa",
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": 10,
            "draw_date": "2026-09-01T19:00:00+00:00",
            "publish_at": "2026-08-01T00:00:00+00:00",
        },
    )
    raffle_id = created.json()["data"]["id"]

    updated = await api_client.put(
        f"{API}/raffles/{raffle_id}", json={"publish_at": "2026-08-15T00:00:00+00:00"}
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["publish_at"].startswith("2026-08-15T00:00:00")


async def test_manual_publish_is_blocked_before_the_scheduled_date(
    api_client: AsyncClient,
) -> None:
    """Regression test: PATCH .../publish used to ignore publish_at entirely,
    letting an admin publish a scheduled raffle early — exactly what happened
    in production. Tickets are generated (the other publish precondition) so
    the schedule is isolated as the only reason it should be blocked."""
    future = (datetime.now(UTC) + timedelta(days=4)).isoformat()
    created = await api_client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa programada futura",
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": 10,
            "draw_date": "2026-09-01T19:00:00+00:00",
            "publish_at": future,
        },
    )
    raffle_id = created.json()["data"]["id"]
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")

    response = await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    assert response.status_code == 409, response.text


async def test_manual_publish_succeeds_once_the_scheduled_date_has_arrived(
    api_client: AsyncClient,
) -> None:
    past = (datetime.now(UTC) - timedelta(minutes=1)).isoformat()
    created = await api_client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa programada ya vencida",
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": 10,
            "draw_date": "2026-09-01T19:00:00+00:00",
            "publish_at": past,
        },
    )
    raffle_id = created.json()["data"]["id"]
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")

    response = await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    assert response.status_code == 200, response.text
    assert response.json()["data"]["status"] == "published"
