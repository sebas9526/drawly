"""End-to-end API tests for the analytics module — real aggregation queries
against the in-memory SQLite test database, going through the actual admin
endpoints (raffle/ticket/participant/collaborator creation) rather than
fabricating rows directly."""

from collections.abc import Awaitable, Callable
from typing import Any

from httpx import AsyncClient

API = "/api/v1"


async def _create_raffle(client: AsyncClient, *, title: str, total: int, price: int) -> str:
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
    assert response.status_code == 201, response.text
    raffle_id: str = response.json()["data"]["id"]
    generated = await client.post(f"{API}/raffles/{raffle_id}/tickets")
    assert generated.status_code == 201, generated.text
    published = await client.patch(f"{API}/raffles/{raffle_id}/publish")
    assert published.status_code == 200, published.text
    return raffle_id


async def _create_participant(client: AsyncClient, *, full_name: str, phone: str) -> str:
    response = await client.post(
        f"{API}/participants", json={"full_name": full_name, "phone": phone}
    )
    assert response.status_code == 201, response.text
    participant_id: str = response.json()["data"]["id"]
    return participant_id


async def _create_collaborator(client: AsyncClient, *, raffle_id: str, name: str) -> str:
    response = await client.post(
        f"{API}/collaborators", json={"raffle_id": raffle_id, "name": name}
    )
    assert response.status_code == 201, response.text
    collaborator_id: str = response.json()["data"]["id"]
    return collaborator_id


async def _first_ticket_id(client: AsyncClient, *, raffle_id: str, number: int) -> str:
    response = await client.get(f"{API}/tickets", params={"raffle_id": raffle_id, "page_size": 100})
    assert response.status_code == 200, response.text
    ticket = next(t for t in response.json()["data"] if t["number"] == number)
    ticket_id: str = ticket["id"]
    return ticket_id


async def _seed_one_paid_sale(client: AsyncClient) -> dict[str, Any]:
    """Raffle of 5 tickets @ 10000; ticket #1 reserved+paid by one participant
    through one collaborator. Returns the ids involved for assertions."""
    raffle_id = await _create_raffle(client, title="Rifa Analytics", total=5, price=10_000)
    participant_id = await _create_participant(client, full_name="Ana", phone="3001111111")
    collaborator_id = await _create_collaborator(client, raffle_id=raffle_id, name="Pedro")
    ticket_id = await _first_ticket_id(client, raffle_id=raffle_id, number=1)

    reserved = await client.patch(
        f"{API}/tickets/{ticket_id}/reserve",
        json={"participant_id": participant_id, "collaborator_id": collaborator_id},
    )
    assert reserved.status_code == 200, reserved.text
    paid = await client.patch(f"{API}/tickets/{ticket_id}/pay")
    assert paid.status_code == 200, paid.text

    return {
        "raffle_id": raffle_id,
        "participant_id": participant_id,
        "collaborator_id": collaborator_id,
        "ticket_id": ticket_id,
    }


async def test_empty_analytics_dashboard(api_client: AsyncClient) -> None:
    response = await api_client.get(f"{API}/analytics/dashboard")
    assert response.status_code == 200, response.text
    data = response.json()["data"]

    assert data["raffles_total"] == 0
    assert data["tickets_paid"] == 0
    assert data["percent_sold"] == 0.0
    assert data["expected_revenue"] == 0.0


async def test_analytics_dashboard_reflects_one_paid_sale(api_client: AsyncClient) -> None:
    await _seed_one_paid_sale(api_client)

    response = await api_client.get(f"{API}/analytics/dashboard")
    assert response.status_code == 200, response.text
    data = response.json()["data"]

    assert data["raffles_total"] == 1
    assert data["raffles_published"] == 1
    assert data["tickets_available"] == 4
    assert data["tickets_reserved"] == 0
    assert data["tickets_paid"] == 1
    assert data["participants_total"] == 1
    assert data["collaborators_total"] == 1
    assert data["expected_revenue"] == 50_000.0  # 5 * 10000
    assert data["received_revenue"] == 10_000.0
    assert data["percent_sold"] == 20.0  # 1 of 5


async def test_analytics_raffles_list_and_detail(api_client: AsyncClient) -> None:
    seed = await _seed_one_paid_sale(api_client)

    listed = await api_client.get(f"{API}/analytics/raffles")
    assert listed.status_code == 200, listed.text
    rows = listed.json()["data"]
    assert len(rows) == 1
    assert rows[0]["paid"] == 1
    assert rows[0]["available"] == 4
    assert rows[0]["percent_sold"] == 20.0
    assert rows[0]["expected_revenue"] == 50_000.0

    detail = await api_client.get(f"{API}/analytics/raffles/{seed['raffle_id']}")
    assert detail.status_code == 200, detail.text
    detail_data = detail.json()["data"]
    assert detail_data["paid"] == 1
    assert [c["id"] for c in detail_data["top_collaborators"]] == [seed["collaborator_id"]]
    assert [p["id"] for p in detail_data["top_participants"]] == [seed["participant_id"]]


async def test_analytics_raffle_detail_404_for_unknown_id(api_client: AsyncClient) -> None:
    response = await api_client.get(f"{API}/analytics/raffles/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


async def test_analytics_collaborators_report(api_client: AsyncClient) -> None:
    seed = await _seed_one_paid_sale(api_client)

    response = await api_client.get(f"{API}/analytics/collaborators")
    assert response.status_code == 200, response.text
    rows = response.json()["data"]
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == seed["collaborator_id"]
    assert row["total_sales"] == 1
    assert row["total_reservations"] == 0
    assert row["participants_served"] == 1
    assert row["expected_amount"] == 10_000.0
    assert row["participation_percent"] == 20.0  # 1 of 5 tickets
    assert row["rank"] == 1


async def test_analytics_collaborators_report_is_paginated_and_preserves_rank(
    api_client: AsyncClient,
) -> None:
    """Rank depends on the full ordered set, so it must stay correct across
    pages instead of restarting at 1 on every page (see AnalyticsUseCases.
    _all_collaborator_rows / list_collaborators)."""
    raffle_a = await _create_raffle(api_client, title="Rifa A", total=2, price=20_000)
    raffle_b = await _create_raffle(api_client, title="Rifa B", total=2, price=10_000)
    collaborator_a = await _create_collaborator(api_client, raffle_id=raffle_a, name="Top")
    collaborator_b = await _create_collaborator(api_client, raffle_id=raffle_b, name="Second")
    participant_id = await _create_participant(api_client, full_name="Ana", phone="3005555555")

    for raffle_id, collaborator_id in ((raffle_a, collaborator_a), (raffle_b, collaborator_b)):
        ticket_id = await _first_ticket_id(api_client, raffle_id=raffle_id, number=1)
        await api_client.patch(
            f"{API}/tickets/{ticket_id}/reserve",
            json={"participant_id": participant_id, "collaborator_id": collaborator_id},
        )
        await api_client.patch(f"{API}/tickets/{ticket_id}/pay")

    page1 = await api_client.get(
        f"{API}/analytics/collaborators", params={"page": 1, "page_size": 1}
    )
    assert page1.status_code == 200, page1.text
    body1 = page1.json()
    assert body1["pagination"] == {"page": 1, "page_size": 1, "total": 2, "total_pages": 2}
    assert len(body1["data"]) == 1
    assert body1["data"][0]["name"] == "Top"
    assert body1["data"][0]["rank"] == 1

    page2 = await api_client.get(
        f"{API}/analytics/collaborators", params={"page": 2, "page_size": 1}
    )
    body2 = page2.json()
    assert len(body2["data"]) == 1
    assert body2["data"][0]["name"] == "Second"
    assert body2["data"][0]["rank"] == 2


async def test_analytics_participants_report(api_client: AsyncClient) -> None:
    seed = await _seed_one_paid_sale(api_client)

    response = await api_client.get(f"{API}/analytics/participants")
    assert response.status_code == 200, response.text
    rows = response.json()["data"]
    assert len(rows) == 1
    row = rows[0]
    assert row["id"] == seed["participant_id"]
    assert row["purchases_count"] == 1
    assert row["tickets_count"] == 1
    assert row["amount_invested"] == 10_000.0
    assert row["raffles_count"] == 1
    assert row["last_purchase_at"] is not None


async def test_analytics_participants_report_is_paginated(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client, title="Rifa", total=2, price=10_000)
    ana = await _create_participant(api_client, full_name="Ana", phone="3001111111")
    beto = await _create_participant(api_client, full_name="Beto", phone="3002222222")
    for number, participant_id in ((1, ana), (2, beto)):
        ticket_id = await _first_ticket_id(api_client, raffle_id=raffle_id, number=number)
        await api_client.patch(
            f"{API}/tickets/{ticket_id}/reserve", json={"participant_id": participant_id}
        )

    page1 = await api_client.get(
        f"{API}/analytics/participants", params={"page": 1, "page_size": 1}
    )
    assert page1.status_code == 200, page1.text
    body1 = page1.json()
    assert body1["pagination"] == {"page": 1, "page_size": 1, "total": 2, "total_pages": 2}
    assert len(body1["data"]) == 1

    page2 = await api_client.get(
        f"{API}/analytics/participants", params={"page": 2, "page_size": 1}
    )
    body2 = page2.json()
    assert len(body2["data"]) == 1
    # The two pages are disjoint halves of the same ordered set.
    assert body1["data"][0]["id"] != body2["data"][0]["id"]


async def test_analytics_sales_global_reports(api_client: AsyncClient) -> None:
    seed = await _seed_one_paid_sale(api_client)

    response = await api_client.get(f"{API}/analytics/sales")
    assert response.status_code == 200, response.text
    data = response.json()["data"]

    assert [c["id"] for c in data["top_collaborators"]] == [seed["collaborator_id"]]
    assert [r["id"] for r in data["top_raffles"]] == [seed["raffle_id"]]
    assert [p["id"] for p in data["top_participants"]] == [seed["participant_id"]]
    assert data["status_distribution"]["paid"] == 1
    assert data["status_distribution"]["available"] == 4
    assert len(data["sales_by_day"]) == 1
    assert data["sales_by_day"][0]["count"] == 1
    assert data["sales_by_day"][0]["value"] == 10_000.0


async def test_analytics_exports_return_downloadable_files(api_client: AsyncClient) -> None:
    await _seed_one_paid_sale(api_client)

    excel = await api_client.get(f"{API}/analytics/dashboard/export", params={"format": "excel"})
    assert excel.status_code == 200, excel.text
    assert excel.headers["content-type"].startswith("application/vnd.openxmlformats")
    assert excel.content[:2] == b"PK"  # .xlsx is a zip archive

    pdf = await api_client.get(f"{API}/analytics/raffles/export", params={"format": "pdf"})
    assert pdf.status_code == 200, pdf.text
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF")


async def test_analytics_never_leaks_another_owners_data(
    client_factory: Callable[[str], Awaitable[AsyncClient]],
) -> None:
    owner = await client_factory("owner-with-sales@drawly.test")
    await _seed_one_paid_sale(owner)
    other = await client_factory("other-owner@drawly.test")

    dashboard = await other.get(f"{API}/analytics/dashboard")
    assert dashboard.status_code == 200, dashboard.text
    assert dashboard.json()["data"]["raffles_total"] == 0

    raffles = await other.get(f"{API}/analytics/raffles")
    assert raffles.json()["data"] == []

    collaborators = await other.get(f"{API}/analytics/collaborators")
    assert collaborators.json()["data"] == []

    participants = await other.get(f"{API}/analytics/participants")
    assert participants.json()["data"] == []
