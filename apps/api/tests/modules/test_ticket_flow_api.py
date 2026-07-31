"""End-to-end API tests for the ticket lifecycle (SQLite-backed).

Covers the acceptance flow: create raffle -> generate tickets -> reserve ->
cancel -> pay, plus the response-envelope contract and conflict rules.
"""

from typing import Any

from httpx import AsyncClient

API = "/api/v1"


async def _create_raffle(
    client: AsyncClient, total_tickets: int = 5, starting_number: int = 1
) -> str:
    response = await client.post(
        f"{API}/raffles",
        json={
            "title": "Gran Rifa 2026",
            "description": "Una rifa de prueba",
            "prize": "Un carro",
            "ticket_price": 10000,
            "total_tickets": total_tickets,
            "starting_number": starting_number,
            "draw_date": "2026-08-01T19:00:00+00:00",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["success"] is True
    assert body["message"]
    return str(body["data"]["id"])


async def _tickets(client: AsyncClient, raffle_id: str) -> list[dict[str, Any]]:
    response = await client.get(f"{API}/tickets", params={"raffle_id": raffle_id, "page_size": 100})
    assert response.status_code == 200, response.text
    return list(response.json()["data"])


async def test_generate_tickets_creates_exact_count(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client, total_tickets=5)

    response = await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["data"]["generated"] == 5

    tickets = await _tickets(api_client, raffle_id)
    assert len(tickets) == 5
    assert [t["number"] for t in tickets] == [1, 2, 3, 4, 5]
    assert all(t["status"] == "available" for t in tickets)


async def test_generate_tickets_honors_starting_number_zero(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client, total_tickets=100, starting_number=0)

    response = await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    assert response.status_code == 201, response.text
    assert response.json()["data"]["generated"] == 100

    tickets = await _tickets(api_client, raffle_id)
    assert min(t["number"] for t in tickets) == 0
    assert max(t["number"] for t in tickets) == 99


async def test_raffle_rejects_invalid_starting_number(api_client: AsyncClient) -> None:
    response = await api_client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa inválida",
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": 10,
            "starting_number": 2,
            "draw_date": "2026-08-01T19:00:00+00:00",
        },
    )
    assert response.status_code == 422


async def test_raffle_starting_number_is_immutable_after_creation(
    api_client: AsyncClient,
) -> None:
    raffle_id = await _create_raffle(api_client, total_tickets=10, starting_number=0)

    # RaffleUpdate has no starting_number field at all (extra="forbid").
    response = await api_client.put(f"{API}/raffles/{raffle_id}", json={"starting_number": 1})
    assert response.status_code == 422


async def test_tickets_cannot_be_generated_twice(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")

    response = await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    assert response.status_code == 409
    assert response.json()["success"] is False


async def test_list_available_only_returns_available(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client, total_tickets=3)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    tickets = await _tickets(api_client, raffle_id)
    await api_client.patch(f"{API}/tickets/{tickets[0]['id']}/reserve", json={})

    response = await api_client.get(f"{API}/tickets/available", params={"raffle_id": raffle_id})
    assert response.status_code == 200
    available = response.json()["data"]
    assert len(available) == 2
    assert all(t["status"] == "available" for t in available)


async def test_reserve_then_reserve_again_conflicts(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    ticket_id = (await _tickets(api_client, raffle_id))[0]["id"]

    first = await api_client.patch(f"{API}/tickets/{ticket_id}/reserve", json={})
    assert first.status_code == 200
    assert first.json()["data"]["status"] == "reserved"
    # Admin-initiated reservations don't auto-expire (only public/customer
    # reservations do) — a deliberate action by the organizer shouldn't
    # silently revert.
    assert first.json()["data"]["expires_at"] is None

    second = await api_client.patch(f"{API}/tickets/{ticket_id}/reserve", json={})
    assert second.status_code == 409


async def test_cancel_returns_ticket_to_available(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    ticket_id = (await _tickets(api_client, raffle_id))[0]["id"]
    await api_client.patch(f"{API}/tickets/{ticket_id}/reserve", json={})

    response = await api_client.patch(f"{API}/tickets/{ticket_id}/cancel")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "available"
    assert data["participant_id"] is None
    assert data["reserved_at"] is None


async def test_paid_ticket_cannot_be_reserved(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    ticket_id = (await _tickets(api_client, raffle_id))[0]["id"]

    await api_client.patch(f"{API}/tickets/{ticket_id}/reserve", json={})
    paid = await api_client.patch(f"{API}/tickets/{ticket_id}/pay")
    assert paid.status_code == 200
    assert paid.json()["data"]["status"] == "paid"

    reserve_again = await api_client.patch(f"{API}/tickets/{ticket_id}/reserve", json={})
    assert reserve_again.status_code == 409


async def test_pay_requires_reservation_first(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    ticket_id = (await _tickets(api_client, raffle_id))[0]["id"]

    response = await api_client.patch(f"{API}/tickets/{ticket_id}/pay")
    assert response.status_code == 409


async def test_get_ticket_detail(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    ticket_id = (await _tickets(api_client, raffle_id))[0]["id"]

    response = await api_client.get(f"{API}/tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == ticket_id


async def test_unknown_ticket_returns_404(api_client: AsyncClient) -> None:
    response = await api_client.get(f"{API}/tickets/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.json()["success"] is False
