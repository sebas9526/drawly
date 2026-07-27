"""API-level contract tests for DELETE /raffles/{id}: soft delete, blocked
once a ticket has a participant assigned (docs/02-architecture/DOMAIN_MODEL.md),
and 404 on an unknown/already-deleted raffle.
"""

from typing import Any

from httpx import AsyncClient

API = "/api/v1"


async def _create_raffle(client: AsyncClient, total_tickets: int = 3) -> str:
    response = await client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa a borrar",
            "description": "",
            "prize": "Premio",
            "ticket_price": 1000,
            "total_tickets": total_tickets,
            "draw_date": "2026-08-01T19:00:00+00:00",
        },
    )
    assert response.status_code == 201, response.text
    return str(response.json()["data"]["id"])


async def _generate_and_list_tickets(client: AsyncClient, raffle_id: str) -> list[dict[str, Any]]:
    await client.post(f"{API}/raffles/{raffle_id}/tickets")
    response = await client.get(f"{API}/tickets", params={"raffle_id": raffle_id, "page_size": 100})
    return list(response.json()["data"])


async def test_delete_raffle_without_participants_succeeds(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)

    response = await api_client.delete(f"{API}/raffles/{raffle_id}")
    assert response.status_code == 200, response.text
    assert response.json()["data"]["deleted"] is True

    follow_up = await api_client.get(f"{API}/raffles/{raffle_id}")
    assert follow_up.status_code == 404


async def test_delete_blocked_when_a_ticket_has_a_participant(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    ticket = (await _generate_and_list_tickets(api_client, raffle_id))[0]

    participant = await api_client.post(
        f"{API}/participants", json={"full_name": "Ana Díaz", "phone": "3001234"}
    )
    pid = participant.json()["data"]["id"]
    assigned = await api_client.patch(
        f"{API}/tickets/{ticket['id']}/participant", json={"participant_id": pid}
    )
    assert assigned.status_code == 200, assigned.text

    blocked = await api_client.delete(f"{API}/raffles/{raffle_id}")
    assert blocked.status_code == 409

    # Releasing the participant unblocks the delete.
    released = await api_client.delete(f"{API}/tickets/{ticket['id']}/participant")
    assert released.status_code == 200

    deleted = await api_client.delete(f"{API}/raffles/{raffle_id}")
    assert deleted.status_code == 200


async def test_delete_unknown_raffle_returns_404(api_client: AsyncClient) -> None:
    response = await api_client.delete(f"{API}/raffles/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


async def test_recreating_a_raffle_reuses_the_deleted_ones_slug(api_client: AsyncClient) -> None:
    """Regression test: public_slug used to carry a table-wide DB UNIQUE
    constraint, which outlived a soft-deleted raffle. Deleting a raffle and
    creating a new one with the same title (same slug candidate) then 500'd
    with an IntegrityError instead of succeeding — exists_slug already
    excluded deleted rows at the app layer, but the DB constraint didn't."""
    first = await api_client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa duplicada",
            "description": "",
            "prize": "Premio",
            "ticket_price": 1000,
            "total_tickets": 3,
            "draw_date": "2026-08-01T19:00:00+00:00",
        },
    )
    assert first.status_code == 201, first.text
    first_data = first.json()["data"]

    deleted = await api_client.delete(f"{API}/raffles/{first_data['id']}")
    assert deleted.status_code == 200

    second = await api_client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa duplicada",
            "description": "",
            "prize": "Premio",
            "ticket_price": 1000,
            "total_tickets": 3,
            "draw_date": "2026-08-01T19:00:00+00:00",
        },
    )
    assert second.status_code == 201, second.text
    assert second.json()["data"]["public_slug"] == first_data["public_slug"]
