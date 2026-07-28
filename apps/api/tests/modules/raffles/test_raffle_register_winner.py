"""API tests for PATCH /raffles/{id}/winner — manual winner registration.

Covers: a paid ticket closes the raffle and is marked WINNER; an unpaid
ticket is recorded as an attempt without closing anything (the organizer can
retry); an unknown number 404s; a draft or already-closed raffle 409s.
"""

from typing import Any

from httpx import AsyncClient

API = "/api/v1"


async def _raffle_with_tickets(client: AsyncClient, *, total: int = 3) -> tuple[str, str]:
    response = await client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa Ganador",
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": total,
            "draw_date": "2026-09-01T19:00:00+00:00",
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    raffle_id, slug = data["id"], data["public_slug"]
    await client.post(f"{API}/raffles/{raffle_id}/tickets")
    return raffle_id, slug


async def _published_raffle_with_tickets(client: AsyncClient, *, total: int = 3) -> str:
    raffle_id, _ = await _raffle_with_tickets(client, total=total)
    published = await client.patch(f"{API}/raffles/{raffle_id}/publish")
    assert published.status_code == 200, published.text
    return raffle_id


async def _first_ticket_id(client: AsyncClient, raffle_id: str) -> str:
    response = await client.get(f"{API}/tickets", params={"raffle_id": raffle_id, "page_size": 1})
    ticket: dict[str, Any] = response.json()["data"][0]
    return str(ticket["id"])


async def _register_winner(client: AsyncClient, raffle_id: str, ticket_number: int) -> Any:
    return await client.patch(
        f"{API}/raffles/{raffle_id}/winner", json={"ticket_number": ticket_number}
    )


async def test_paid_ticket_becomes_winner_and_closes_the_raffle(api_client: AsyncClient) -> None:
    raffle_id = await _published_raffle_with_tickets(api_client)
    ticket_id = await _first_ticket_id(api_client, raffle_id)
    await api_client.patch(f"{API}/tickets/{ticket_id}/reserve", json={})
    await api_client.patch(f"{API}/tickets/{ticket_id}/pay")

    response = await _register_winner(api_client, raffle_id, 1)
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["valid"] is True
    assert data["ticket_number"] == 1
    assert data["winner_at"] is not None

    raffle = (await api_client.get(f"{API}/raffles/{raffle_id}")).json()["data"]
    assert raffle["status"] == "closed"
    assert raffle["closed_at"] is not None
    assert raffle["winner_ticket_id"] == ticket_id

    ticket = (await api_client.get(f"{API}/tickets/{ticket_id}")).json()["data"]
    assert ticket["status"] == "winner"


async def test_unpaid_ticket_is_recorded_but_does_not_close_the_raffle(
    api_client: AsyncClient,
) -> None:
    raffle_id = await _published_raffle_with_tickets(api_client)
    # Ticket #1 stays AVAILABLE — never reserved or paid.

    response = await _register_winner(api_client, raffle_id, 1)
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["valid"] is False
    assert data["winner_at"] is None

    raffle = (await api_client.get(f"{API}/raffles/{raffle_id}")).json()["data"]
    assert raffle["status"] == "published"
    assert raffle["closed_at"] is None
    assert raffle["winner_ticket_id"] is not None  # attempt recorded

    # The organizer can just retry with another number afterward.
    ticket_id = await _first_ticket_id(api_client, raffle_id)
    await api_client.patch(f"{API}/tickets/{ticket_id}/reserve", json={})
    await api_client.patch(f"{API}/tickets/{ticket_id}/pay")
    retry = await _register_winner(api_client, raffle_id, 1)
    assert retry.status_code == 200, retry.text
    assert retry.json()["data"]["valid"] is True


async def test_unknown_ticket_number_returns_404(api_client: AsyncClient) -> None:
    raffle_id = await _published_raffle_with_tickets(api_client, total=3)
    response = await _register_winner(api_client, raffle_id, 999)
    assert response.status_code == 404, response.text


async def test_cannot_register_winner_on_a_draft_raffle(api_client: AsyncClient) -> None:
    raffle_id, _ = await _raffle_with_tickets(api_client)
    response = await _register_winner(api_client, raffle_id, 1)
    assert response.status_code == 409, response.text


async def test_cannot_register_winner_twice(api_client: AsyncClient) -> None:
    raffle_id = await _published_raffle_with_tickets(api_client)
    ticket_id = await _first_ticket_id(api_client, raffle_id)
    await api_client.patch(f"{API}/tickets/{ticket_id}/reserve", json={})
    await api_client.patch(f"{API}/tickets/{ticket_id}/pay")
    first = await _register_winner(api_client, raffle_id, 1)
    assert first.status_code == 200, first.text

    again = await _register_winner(api_client, raffle_id, 1)
    assert again.status_code == 409, again.text
