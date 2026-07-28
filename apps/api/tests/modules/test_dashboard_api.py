"""End-to-end API test for the aggregated dashboard overview."""

from typing import Any

from httpx import AsyncClient

API = "/api/v1"


async def _raffle(
    client: AsyncClient, *, title: str, total: int, price: int, publish: bool
) -> tuple[str, str]:
    response = await client.post(
        f"{API}/raffles",
        json={
            "title": title,
            "description": "",
            "prize": "x",
            "ticket_price": price,
            "total_tickets": total,
            "draw_date": "2026-09-01T19:00:00+00:00",
        },
    )
    data = response.json()["data"]
    raffle_id, slug = data["id"], data["public_slug"]
    await client.post(f"{API}/raffles/{raffle_id}/tickets")
    if publish:
        await client.patch(f"{API}/raffles/{raffle_id}/publish")
    return raffle_id, slug


async def _public_reserve(
    client: AsyncClient, slug: str, number: int, *, phone: str, name: str, collaborator_id: str
) -> Any:
    return await client.post(
        f"{API}/public/raffles/{slug}/reserve",
        json={
            "ticket_number": number,
            "participant": {"full_name": name, "phone": phone},
            "collaborator_id": collaborator_id,
        },
    )


async def test_empty_dashboard(api_client: AsyncClient) -> None:
    response = await api_client.get(f"{API}/dashboard/overview")
    assert response.status_code == 200, response.text
    data = response.json()["data"]

    assert data["raffles"]["total"] == 0
    assert data["tickets"]["total"] == 0
    assert data["participants"] == 0
    assert data["sales"]["potential_value"] == 0
    assert data["recent_reservations"] == []
    assert data["recent_raffles"] == []


async def test_dashboard_reflects_business_state(api_client: AsyncClient) -> None:
    # Published raffle A (5 x 20000) and draft raffle B (3 x 10000).
    raffle_a_id, slug_a = await _raffle(
        api_client, title="Rifa A", total=5, price=20000, publish=True
    )
    await _raffle(api_client, title="Rifa B", total=3, price=10000, publish=False)
    collaborator = await api_client.post(
        f"{API}/collaborators",
        json={"raffle_ids": [raffle_a_id], "name": "Vendedor", "color": "#4F46E5"},
    )
    collaborator_id = collaborator.json()["data"]["id"]

    # Two public reservations on A with distinct participants.
    assert (
        await _public_reserve(
            api_client, slug_a, 1, phone="3001", name="Ana", collaborator_id=collaborator_id
        )
    ).status_code == 201
    assert (
        await _public_reserve(
            api_client, slug_a, 2, phone="3002", name="Beto", collaborator_id=collaborator_id
        )
    ).status_code == 201

    data = (await api_client.get(f"{API}/dashboard/overview")).json()["data"]

    assert data["raffles"] == {
        "total": 2,
        "active": 2,
        "draft": 1,
        "published": 1,
        "closed": 0,
        "archived": 0,
    }
    assert data["tickets"]["total"] == 8
    assert data["tickets"]["available"] == 6
    assert data["tickets"]["reserved"] == 2
    assert data["tickets"]["paid"] == 0
    assert data["participants"] == 2

    assert data["sales"]["potential_value"] == 130000  # 5*20000 + 3*10000
    assert data["sales"]["reserved_value"] == 40000  # 2 * 20000
    assert data["sales"]["paid_value"] == 0

    reservations = data["recent_reservations"]
    assert len(reservations) == 2
    assert {r["number"] for r in reservations} == {1, 2}
    assert all(r["raffle_title"] == "Rifa A" for r in reservations)
    assert {r["participant_name"] for r in reservations} == {"Ana", "Beto"}

    raffles = data["recent_raffles"]
    assert len(raffles) == 2
    titles = {r["title"] for r in raffles}
    assert titles == {"Rifa A", "Rifa B"}
    by_title = {r["title"]: r for r in raffles}
    assert by_title["Rifa A"]["available_count"] == 3  # 5 - 2 reserved
    assert by_title["Rifa B"]["status"] == "draft"
