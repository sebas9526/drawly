"""API-level contract tests for DELETE /raffles/{id}: a real, permanent
delete (the raffle row and its tickets are actually gone, not soft-deleted),
blocked once a ticket has a participant assigned
(docs/02-architecture/DOMAIN_MODEL.md), and 404 on an unknown/already-deleted
raffle.
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
    # Tickets can only be assigned once the raffle is published.
    await api_client.patch(f"{API}/raffles/{raffle_id}/publish")

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


async def test_delete_raffle_hard_deletes_its_tickets_too(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client, total_tickets=3)
    tickets = await _generate_and_list_tickets(api_client, raffle_id)
    ticket_id = tickets[0]["id"]

    deleted = await api_client.delete(f"{API}/raffles/{raffle_id}")
    assert deleted.status_code == 200, deleted.text

    # The ticket is gone too, not just the raffle — a real delete, not a
    # soft-deleted row still sitting in the database.
    ticket_lookup = await api_client.get(f"{API}/tickets/{ticket_id}")
    assert ticket_lookup.status_code == 404

    remaining = await api_client.get(f"{API}/tickets", params={"raffle_id": raffle_id})
    assert remaining.json()["data"] == []


async def test_delete_closed_raffle_with_a_confirmed_winner(api_client: AsyncClient) -> None:
    """A CLOSED raffle's winning ticket has no participant attached in this
    scenario (reserved/paid anonymously), so the participant guard doesn't
    block it — this exercises the trickier path: raffle.winner_ticket_id FKs
    into the very ticket being hard-deleted, so it must be cleared first."""
    raffle_id = await _create_raffle(api_client, total_tickets=3)
    tickets = await _generate_and_list_tickets(api_client, raffle_id)
    ticket_id = tickets[0]["id"]
    await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    await api_client.patch(f"{API}/tickets/{ticket_id}/reserve", json={})
    await api_client.patch(f"{API}/tickets/{ticket_id}/pay")
    winner = await api_client.patch(f"{API}/raffles/{raffle_id}/winner", json={"ticket_number": 1})
    assert winner.status_code == 200, winner.text
    assert winner.json()["data"]["valid"] is True

    deleted = await api_client.delete(f"{API}/raffles/{raffle_id}")
    assert deleted.status_code == 200, deleted.text

    ticket_lookup = await api_client.get(f"{API}/tickets/{ticket_id}")
    assert ticket_lookup.status_code == 404


async def test_delete_raffle_cascades_its_collaborator_link_but_keeps_the_collaborator(
    api_client: AsyncClient,
) -> None:
    """collaborator_raffles is cleaned up by the DB itself (ON DELETE
    CASCADE, migration 0012) — the collaborator entity itself, a separate
    aggregate, must survive untouched."""
    raffle_id = await _create_raffle(api_client)
    collaborator = await api_client.post(
        f"{API}/collaborators",
        json={"raffle_ids": [raffle_id], "name": "Ana", "color": "#4F46E5"},
    )
    assert collaborator.status_code == 201, collaborator.text
    collaborator_id = collaborator.json()["data"]["id"]

    deleted = await api_client.delete(f"{API}/raffles/{raffle_id}")
    assert deleted.status_code == 200, deleted.text

    refreshed = await api_client.get(f"{API}/collaborators/{collaborator_id}")
    assert refreshed.status_code == 200, refreshed.text
    assert refreshed.json()["data"]["raffle_ids"] == []


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
