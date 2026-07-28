"""Regression tests: reserving, paying, or assigning a participant to a
ticket used to work regardless of the raffle's status — an organizer could
manage tickets on a raffle still in draft (including one waiting on a
scheduled publish_at), even though nothing is visible to real participants
until the raffle is actually published. Confirmed live: a raffle scheduled
for a future date showed reservable tickets in the admin "Gestionar
boletas" screen. Tickets now require the raffle to be PUBLISHED first.
"""

from httpx import AsyncClient

API = "/api/v1"


async def _create_raffle(client: AsyncClient) -> str:
    response = await client.post(
        f"{API}/raffles",
        json={
            "title": "Rifa sin publicar",
            "description": "",
            "prize": "x",
            "ticket_price": 1000,
            "total_tickets": 5,
            "draw_date": "2026-09-01T19:00:00+00:00",
        },
    )
    assert response.status_code == 201, response.text
    return str(response.json()["data"]["id"])


async def _first_ticket_id(client: AsyncClient, raffle_id: str) -> str:
    response = await client.get(f"{API}/tickets", params={"raffle_id": raffle_id, "page_size": 1})
    return str(response.json()["data"][0]["id"])


async def test_reserve_is_blocked_before_the_raffle_is_published(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    ticket_id = await _first_ticket_id(api_client, raffle_id)

    response = await api_client.patch(f"{API}/tickets/{ticket_id}/reserve", json={})
    assert response.status_code == 409, response.text


async def test_assign_participant_is_blocked_before_the_raffle_is_published(
    api_client: AsyncClient,
) -> None:
    raffle_id = await _create_raffle(api_client)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    ticket_id = await _first_ticket_id(api_client, raffle_id)

    participant = await api_client.post(
        f"{API}/participants", json={"full_name": "Ana Díaz", "phone": "3001234"}
    )
    pid = participant.json()["data"]["id"]

    response = await api_client.patch(
        f"{API}/tickets/{ticket_id}/participant", json={"participant_id": pid}
    )
    assert response.status_code == 409, response.text


async def test_ticket_actions_work_once_the_raffle_is_published(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    ticket_id = await _first_ticket_id(api_client, raffle_id)

    reserved = await api_client.patch(f"{API}/tickets/{ticket_id}/reserve", json={})
    assert reserved.status_code == 200, reserved.text

    paid = await api_client.patch(f"{API}/tickets/{ticket_id}/pay")
    assert paid.status_code == 200, paid.text
    assert paid.json()["data"]["status"] == "paid"
