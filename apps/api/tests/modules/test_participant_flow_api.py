"""End-to-end API tests for participants + their integration with tickets."""

from typing import Any

from httpx import AsyncClient

API = "/api/v1"


async def _create_raffle(client: AsyncClient, total_tickets: int = 3) -> str:
    response = await client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa P",
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
    # Tickets can only be reserved/assigned once the raffle is published.
    await client.patch(f"{API}/raffles/{raffle_id}/publish")
    response = await client.get(f"{API}/tickets", params={"raffle_id": raffle_id, "page_size": 100})
    return list(response.json()["data"])


async def _create_participant(
    client: AsyncClient, *, full_name: str = "Ana Díaz", phone: str = "3001234", **extra: Any
) -> dict[str, Any]:
    response = await client.post(
        f"{API}/participants", json={"full_name": full_name, "phone": phone, **extra}
    )
    assert response.status_code == 201, response.text
    return dict(response.json()["data"])


async def test_create_participant_returns_envelope(api_client: AsyncClient) -> None:
    data = await _create_participant(api_client, document="CC-99")
    assert data["full_name"] == "Ana Díaz"
    assert data["ticket_count"] == 0
    assert data["document"] == "CC-99"


async def test_duplicate_phone_is_rejected(api_client: AsyncClient) -> None:
    await _create_participant(api_client, phone="3005555")
    response = await api_client.post(
        f"{API}/participants", json={"full_name": "Other", "phone": "3005555"}
    )
    assert response.status_code == 409


async def test_edit_participant(api_client: AsyncClient) -> None:
    participant = await _create_participant(api_client)
    response = await api_client.patch(
        f"{API}/participants/{participant['id']}", json={"city": "Bogotá"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["city"] == "Bogotá"


async def test_search_by_name_and_document(api_client: AsyncClient) -> None:
    await _create_participant(
        api_client, full_name="Carlos Ruiz", phone="3009991", document="DOC-7"
    )

    by_name = await api_client.get(f"{API}/participants", params={"search": "Carlos"})
    assert any(p["full_name"] == "Carlos Ruiz" for p in by_name.json()["data"])

    by_doc = await api_client.get(f"{API}/participants", params={"search": "DOC-7"})
    assert any(p["document"] == "DOC-7" for p in by_doc.json()["data"])


async def test_assign_participant_to_multiple_tickets(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client, total_tickets=3)
    tickets = await _generate_and_list_tickets(api_client, raffle_id)
    participant = await _create_participant(api_client)
    pid = participant["id"]

    for ticket in tickets[:2]:
        response = await api_client.patch(
            f"{API}/tickets/{ticket['id']}/participant", json={"participant_id": pid}
        )
        assert response.status_code == 200, response.text
        body = response.json()["data"]
        assert body["status"] == "reserved"
        assert body["participant_id"] == pid
        # Regression: this used to be set to a fixed 48h-from-now TTL and get
        # silently released by the reservation sweep — it must track the
        # raffle's own draw_date instead, which is weeks away here.
        assert body["expires_at"] == "2026-08-01T19:00:00"

    history = await api_client.get(f"{API}/participants/{pid}/tickets")
    assert history.status_code == 200
    assert len(history.json()["data"]) == 2

    detail = await api_client.get(f"{API}/participants/{pid}")
    assert detail.json()["data"]["ticket_count"] == 2
    assert sorted(detail.json()["data"]["ticket_numbers"]) == sorted(
        t["number"] for t in tickets[:2]
    )


async def test_ticket_numbers_appear_in_the_participants_list(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client, total_tickets=3)
    tickets = await _generate_and_list_tickets(api_client, raffle_id)
    with_tickets = await _create_participant(api_client, phone="3003333")
    without_tickets = await _create_participant(
        api_client, full_name="Sin boletas", phone="3004444"
    )

    for ticket in tickets[:2]:
        await api_client.patch(
            f"{API}/tickets/{ticket['id']}/participant",
            json={"participant_id": with_tickets["id"]},
        )

    listed = await api_client.get(f"{API}/participants")
    rows = {row["id"]: row for row in listed.json()["data"]}
    assert sorted(rows[with_tickets["id"]]["ticket_numbers"]) == sorted(
        t["number"] for t in tickets[:2]
    )
    assert rows[without_tickets["id"]]["ticket_numbers"] == []


async def _create_collaborator(client: AsyncClient, raffle_id: str, *, name: str) -> dict[str, Any]:
    response = await client.post(
        f"{API}/collaborators",
        json={"raffle_ids": [raffle_id], "name": name, "color": "#4F46E5"},
    )
    assert response.status_code == 201, response.text
    return dict(response.json()["data"])


async def test_collaborator_names_show_who_sold_each_ticket(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client, total_tickets=3)
    tickets = await _generate_and_list_tickets(api_client, raffle_id)
    ana = await _create_collaborator(api_client, raffle_id, name="Ana")
    beto = await _create_collaborator(api_client, raffle_id, name="Beto")
    participant = await _create_participant(api_client)
    pid = participant["id"]

    # Two tickets sold by two different collaborators, one with none at all.
    await api_client.patch(
        f"{API}/tickets/{tickets[0]['id']}/participant", json={"participant_id": pid}
    )
    await api_client.patch(
        f"{API}/tickets/{tickets[0]['id']}/collaborator", json={"collaborator_id": ana["id"]}
    )
    await api_client.patch(
        f"{API}/tickets/{tickets[1]['id']}/participant", json={"participant_id": pid}
    )
    await api_client.patch(
        f"{API}/tickets/{tickets[1]['id']}/collaborator", json={"collaborator_id": beto["id"]}
    )
    await api_client.patch(
        f"{API}/tickets/{tickets[2]['id']}/participant", json={"participant_id": pid}
    )

    detail = await api_client.get(f"{API}/participants/{pid}")
    assert detail.json()["data"]["collaborator_names"] == ["Ana", "Beto"]

    listed = await api_client.get(f"{API}/participants")
    row = next(p for p in listed.json()["data"] if p["id"] == pid)
    assert row["collaborator_names"] == ["Ana", "Beto"]


async def test_participant_without_a_collaborator_has_no_seller(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    ticket = (await _generate_and_list_tickets(api_client, raffle_id))[0]
    participant = await _create_participant(api_client)
    await api_client.patch(
        f"{API}/tickets/{ticket['id']}/participant", json={"participant_id": participant["id"]}
    )

    detail = await api_client.get(f"{API}/participants/{participant['id']}")
    assert detail.json()["data"]["collaborator_names"] == []


async def test_ticket_has_single_participant_and_can_be_changed(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    ticket = (await _generate_and_list_tickets(api_client, raffle_id))[0]
    first = await _create_participant(api_client, phone="3001111")
    second = await _create_participant(api_client, phone="3002222")

    await api_client.patch(
        f"{API}/tickets/{ticket['id']}/participant", json={"participant_id": first["id"]}
    )
    changed = await api_client.patch(
        f"{API}/tickets/{ticket['id']}/participant", json={"participant_id": second["id"]}
    )
    assert changed.status_code == 200
    assert changed.json()["data"]["participant_id"] == second["id"]

    # The first participant no longer owns the ticket.
    first_history = await api_client.get(f"{API}/participants/{first['id']}/tickets")
    assert first_history.json()["data"] == []


async def test_assigning_unknown_participant_returns_404(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    ticket = (await _generate_and_list_tickets(api_client, raffle_id))[0]
    response = await api_client.patch(
        f"{API}/tickets/{ticket['id']}/participant",
        json={"participant_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 404


async def test_delete_blocked_when_participant_has_tickets(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    ticket = (await _generate_and_list_tickets(api_client, raffle_id))[0]
    participant = await _create_participant(api_client)
    pid = participant["id"]

    await api_client.patch(
        f"{API}/tickets/{ticket['id']}/participant", json={"participant_id": pid}
    )

    blocked = await api_client.delete(f"{API}/participants/{pid}")
    assert blocked.status_code == 409

    # Removing the participant releases the ticket back to available...
    released = await api_client.delete(f"{API}/tickets/{ticket['id']}/participant")
    assert released.status_code == 200
    assert released.json()["data"]["status"] == "available"

    # ...and now the participant can be deleted.
    deleted = await api_client.delete(f"{API}/participants/{pid}")
    assert deleted.status_code == 200
