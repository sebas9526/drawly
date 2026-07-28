"""API tests for GET /public/collaborators/{id}/raffles — the personal
referral link's raffle resolution (used by the frontend's /ref/[id] page)."""

import uuid

from httpx import AsyncClient

API = "/api/v1"


async def _published_raffle(client: AsyncClient, *, title: str = "Rifa") -> str:
    response = await client.post(
        f"{API}/raffles",
        json={
            "title": title,
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": 3,
            "draw_date": "2026-09-01T19:00:00+00:00",
        },
    )
    raffle_id = response.json()["data"]["id"]
    await client.post(f"{API}/raffles/{raffle_id}/tickets")
    published = await client.patch(f"{API}/raffles/{raffle_id}/publish")
    assert published.status_code == 200, published.text
    return str(raffle_id)


async def _collaborator(
    client: AsyncClient, raffle_ids: list[str], *, is_active: bool = True
) -> str:
    response = await client.post(
        f"{API}/collaborators",
        json={"raffle_ids": raffle_ids, "name": "Ana", "is_active": is_active},
    )
    assert response.status_code == 201, response.text
    return str(response.json()["data"]["id"])


async def test_referral_raffles_for_unknown_collaborator_returns_404(
    api_client: AsyncClient,
) -> None:
    response = await api_client.get(f"{API}/public/collaborators/{uuid.uuid4()}/raffles")
    assert response.status_code == 404


async def test_referral_raffles_for_inactive_collaborator_returns_404(
    api_client: AsyncClient,
) -> None:
    raffle_id = await _published_raffle(api_client)
    collaborator_id = await _collaborator(api_client, [raffle_id], is_active=False)

    response = await api_client.get(f"{API}/public/collaborators/{collaborator_id}/raffles")
    assert response.status_code == 404


async def test_referral_raffles_empty_when_no_published_raffle(api_client: AsyncClient) -> None:
    draft = await api_client.post(
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
    draft_id = draft.json()["data"]["id"]
    collaborator_id = await _collaborator(api_client, [draft_id])

    response = await api_client.get(f"{API}/public/collaborators/{collaborator_id}/raffles")
    assert response.status_code == 200, response.text
    assert response.json()["data"] == []


async def test_referral_raffles_returns_a_single_published_raffle(api_client: AsyncClient) -> None:
    raffle_id = await _published_raffle(api_client, title="Rifa Única")
    collaborator_id = await _collaborator(api_client, [raffle_id])

    response = await api_client.get(f"{API}/public/collaborators/{collaborator_id}/raffles")
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["title"] == "Rifa Única"
    assert "public_slug" in data[0]


async def test_referral_raffles_returns_several_published_raffles(api_client: AsyncClient) -> None:
    raffle_a = await _published_raffle(api_client, title="Rifa A")
    raffle_b = await _published_raffle(api_client, title="Rifa B")
    collaborator_id = await _collaborator(api_client, [raffle_a, raffle_b])

    response = await api_client.get(f"{API}/public/collaborators/{collaborator_id}/raffles")
    assert response.status_code == 200, response.text
    titles = {r["title"] for r in response.json()["data"]}
    assert titles == {"Rifa A", "Rifa B"}
