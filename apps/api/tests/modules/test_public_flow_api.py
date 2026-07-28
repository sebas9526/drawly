"""End-to-end API tests for the public reservation portal."""

import uuid
from typing import Any

from httpx import AsyncClient

API = "/api/v1"


async def _published_raffle(client: AsyncClient, total_tickets: int = 5) -> tuple[str, str, str]:
    """Create -> generate tickets -> add a collaborator -> publish. Returns
    (raffle_id, public_slug, collaborator_id) — a collaborator is required on
    every public reserve call now."""
    response = await client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa Pública",
            "description": "Una rifa de prueba",
            "prize": "Un viaje",
            "ticket_price": 5000,
            "total_tickets": total_tickets,
            "draw_date": "2026-09-01T19:00:00+00:00",
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    raffle_id, slug = data["id"], data["public_slug"]
    await client.post(f"{API}/raffles/{raffle_id}/tickets")
    collaborator = await client.post(
        f"{API}/collaborators",
        json={"raffle_ids": [raffle_id], "name": "Vendedor", "color": "#4F46E5"},
    )
    assert collaborator.status_code == 201, collaborator.text
    published = await client.patch(f"{API}/raffles/{raffle_id}/publish")
    assert published.status_code == 200, published.text
    return raffle_id, slug, collaborator.json()["data"]["id"]


async def _reserve(
    client: AsyncClient,
    slug: str,
    number: int,
    *,
    phone: str,
    name: str = "Ana",
    collaborator_id: str | None = None,
) -> Any:
    return await client.post(
        f"{API}/public/raffles/{slug}/reserve",
        json={
            "ticket_number": number,
            "participant": {"full_name": name, "phone": phone},
            "collaborator_id": collaborator_id or str(uuid.uuid4()),
        },
    )


async def test_get_public_raffle_exposes_info_not_internals(api_client: AsyncClient) -> None:
    _, slug, _ = await _published_raffle(api_client, total_tickets=5)

    response = await api_client.get(f"{API}/public/raffles/{slug}")
    assert response.status_code == 200, response.text
    data = response.json()["data"]

    assert data["title"] == "Rifa Pública"
    assert data["total_tickets"] == 5
    assert data["available_count"] == 5
    assert data["reserved_count"] == 0
    assert data["paid_count"] == 0
    # No internal / admin fields leak.
    assert "id" not in data
    assert "organization_id" not in data
    assert "status" not in data


async def test_draft_raffle_is_not_public(api_client: AsyncClient) -> None:
    response = await api_client.post(
        f"{API}/raffles",
        json={
            "title": "Borrador",
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": 3,
            "draw_date": "2026-09-01T19:00:00+00:00",
        },
    )
    slug = response.json()["data"]["public_slug"]
    public = await api_client.get(f"{API}/public/raffles/{slug}")
    assert public.status_code == 404


async def test_unknown_slug_returns_404(api_client: AsyncClient) -> None:
    response = await api_client.get(f"{API}/public/raffles/does-not-exist")
    assert response.status_code == 404


async def test_public_tickets_expose_only_number_and_status(api_client: AsyncClient) -> None:
    _, slug, _ = await _published_raffle(api_client, total_tickets=3)
    response = await api_client.get(f"{API}/public/raffles/{slug}/tickets")
    assert response.status_code == 200
    tickets = response.json()["data"]
    assert len(tickets) == 3
    for ticket in tickets:
        assert set(ticket.keys()) == {"number", "status"}
        assert ticket["status"] == "available"


async def test_public_tickets_are_paginated(api_client: AsyncClient) -> None:
    _, slug, _ = await _published_raffle(api_client, total_tickets=3)
    response = await api_client.get(
        f"{API}/public/raffles/{slug}/tickets", params={"page": 1, "page_size": 2}
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["data"]) == 2
    assert body["pagination"] == {"page": 1, "page_size": 2, "total": 3, "total_pages": 2}


async def test_reserve_available_ticket(api_client: AsyncClient) -> None:
    _, slug, collaborator_id = await _published_raffle(api_client)
    response = await _reserve(api_client, slug, 1, phone="3001000", collaborator_id=collaborator_id)
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    assert data["ticket_number"] == 1
    assert data["status"] == "reserved"
    assert data["raffle_title"] == "Rifa Pública"


async def test_reserve_without_collaborator_is_rejected(api_client: AsyncClient) -> None:
    _, slug, _ = await _published_raffle(api_client)
    response = await api_client.post(
        f"{API}/public/raffles/{slug}/reserve",
        json={"ticket_number": 1, "participant": {"full_name": "Ana", "phone": "3001000"}},
    )
    assert response.status_code == 422, response.text


async def test_cannot_reserve_the_same_ticket_twice(api_client: AsyncClient) -> None:
    _, slug, collaborator_id = await _published_raffle(api_client)
    first = await _reserve(api_client, slug, 1, phone="3001111", collaborator_id=collaborator_id)
    assert first.status_code == 201
    second = await _reserve(api_client, slug, 1, phone="3002222", collaborator_id=collaborator_id)
    assert second.status_code == 409


async def test_reserve_reuses_existing_participant_by_phone(api_client: AsyncClient) -> None:
    _, slug, collaborator_id = await _published_raffle(api_client)
    await _reserve(
        api_client, slug, 1, phone="3009999", name="Ana", collaborator_id=collaborator_id
    )
    await _reserve(
        api_client, slug, 2, phone="3009999", name="Ana", collaborator_id=collaborator_id
    )

    participants = (
        await api_client.get(f"{API}/participants", params={"search": "3009999"})
    ).json()["data"]
    matches = [p for p in participants if p["phone"] == "3009999"]
    assert len(matches) == 1
    assert matches[0]["ticket_count"] == 2


async def test_reserve_unknown_number_returns_404(api_client: AsyncClient) -> None:
    _, slug, collaborator_id = await _published_raffle(api_client, total_tickets=3)
    response = await _reserve(
        api_client, slug, 999, phone="3003333", collaborator_id=collaborator_id
    )
    assert response.status_code == 404


async def test_reserve_on_unpublished_raffle_returns_404(api_client: AsyncClient) -> None:
    response = await api_client.post(
        f"{API}/raffles",
        json={
            "title": "Sin publicar",
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": 3,
            "draw_date": "2026-09-01T19:00:00+00:00",
        },
    )
    raffle_id = response.json()["data"]["id"]
    slug = response.json()["data"]["public_slug"]
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    # Not published yet -> reserve must 404.
    reserve = await _reserve(api_client, slug, 1, phone="3004444")
    assert reserve.status_code == 404


async def test_closed_raffle_stays_public_and_announces_the_winner(
    api_client: AsyncClient,
) -> None:
    raffle_id, slug, collaborator_id = await _published_raffle(api_client, total_tickets=3)
    reserved = await _reserve(
        api_client, slug, 1, phone="3005555", name="Ana Díaz", collaborator_id=collaborator_id
    )
    ticket_id = reserved.json()["data"]["ticket_number"]
    tickets = (await api_client.get(f"{API}/tickets", params={"raffle_id": raffle_id})).json()[
        "data"
    ]
    paid_ticket = next(t for t in tickets if t["number"] == ticket_id)
    await api_client.patch(f"{API}/tickets/{paid_ticket['id']}/pay")
    winner = await api_client.patch(f"{API}/raffles/{raffle_id}/winner", json={"ticket_number": 1})
    assert winner.status_code == 200, winner.text

    public = await api_client.get(f"{API}/public/raffles/{slug}")
    assert public.status_code == 200, public.text
    data = public.json()["data"]
    assert data["winner_ticket_number"] == 1
    assert data["winner_participant_name"] == "Ana Díaz"


async def test_publish_requires_generated_tickets(api_client: AsyncClient) -> None:
    response = await api_client.post(
        f"{API}/raffles",
        json={
            "title": "Sin boletas",
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": 3,
            "draw_date": "2026-09-01T19:00:00+00:00",
        },
    )
    raffle_id = response.json()["data"]["id"]
    publish = await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    assert publish.status_code == 409
