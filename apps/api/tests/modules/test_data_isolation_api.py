"""Cross-user data-isolation tests (SQLite-backed).

The critical multi-tenant guarantee: every admin surface returns ONLY the
authenticated user's data. User A must never see, fetch, or mutate user B's
raffles, tickets, participants, or dashboard aggregates. Both clients run against
one shared database via the ``client_factory`` fixture.
"""

from collections.abc import Awaitable, Callable

from httpx import AsyncClient

API = "/api/v1"

ClientFactory = Callable[[str], Awaitable[AsyncClient]]


async def _create_raffle(client: AsyncClient, title: str, total: int = 5) -> str:
    response = await client.post(
        f"{API}/raffles",
        json={
            "title": title,
            "description": "iso",
            "prize": "prize",
            "ticket_price": 1000,
            "total_tickets": total,
            "draw_date": "2026-08-01T19:00:00+00:00",
        },
    )
    assert response.status_code == 201, response.text
    return str(response.json()["data"]["id"])


async def test_raffles_are_isolated_per_user(client_factory: ClientFactory) -> None:
    alice = await client_factory("alice@drawly.test")
    bob = await client_factory("bob@drawly.test")

    alice_raffle = await _create_raffle(alice, "Alice Raffle")
    await _create_raffle(bob, "Bob Raffle")

    # Each user's list contains only their own raffle.
    alice_list = (await alice.get(f"{API}/raffles")).json()["data"]
    bob_list = (await bob.get(f"{API}/raffles")).json()["data"]
    assert [r["title"] for r in alice_list] == ["Alice Raffle"]
    assert [r["title"] for r in bob_list] == ["Bob Raffle"]

    # Bob cannot fetch Alice's raffle by id: it 404s (existence is not leaked).
    cross = await bob.get(f"{API}/raffles/{alice_raffle}")
    assert cross.status_code == 404
    assert cross.json()["success"] is False


async def test_tickets_are_isolated_per_user(client_factory: ClientFactory) -> None:
    alice = await client_factory("alice@drawly.test")
    bob = await client_factory("bob@drawly.test")

    alice_raffle = await _create_raffle(alice, "Alice Raffle")
    await alice.post(f"{API}/raffles/{alice_raffle}/tickets")

    # Bob lists tickets filtered by Alice's raffle id and sees nothing.
    bob_tickets = await bob.get(f"{API}/tickets", params={"raffle_id": alice_raffle})
    assert bob_tickets.status_code == 200
    assert bob_tickets.json()["data"] == []

    # Alice sees her own tickets.
    alice_tickets = await alice.get(f"{API}/tickets", params={"raffle_id": alice_raffle})
    assert len(alice_tickets.json()["data"]) == 5

    # Bob cannot reserve a ticket he doesn't own (404, not a successful reserve).
    alice_ticket_id = alice_tickets.json()["data"][0]["id"]
    reserve = await bob.patch(f"{API}/tickets/{alice_ticket_id}/reserve", json={})
    assert reserve.status_code == 404


async def test_participants_are_isolated_per_user(client_factory: ClientFactory) -> None:
    alice = await client_factory("alice@drawly.test")
    bob = await client_factory("bob@drawly.test")

    created = await alice.post(
        f"{API}/participants",
        json={"full_name": "Alice Participant", "phone": "3000000000"},
    )
    assert created.status_code == 201, created.text
    participant_id = created.json()["data"]["id"]

    # Bob's participant list is empty; he cannot fetch Alice's participant.
    bob_list = await bob.get(f"{API}/participants")
    assert bob_list.json()["data"] == []
    cross = await bob.get(f"{API}/participants/{participant_id}")
    assert cross.status_code == 404


async def test_dashboard_is_isolated_per_user(client_factory: ClientFactory) -> None:
    alice = await client_factory("alice@drawly.test")
    bob = await client_factory("bob@drawly.test")

    raffle = await _create_raffle(alice, "Alice Raffle", total=7)
    await alice.post(f"{API}/raffles/{raffle}/tickets")

    alice_overview = (await alice.get(f"{API}/dashboard/overview")).json()["data"]
    bob_overview = (await bob.get(f"{API}/dashboard/overview")).json()["data"]

    assert alice_overview["raffles"]["total"] == 1
    assert alice_overview["tickets"]["total"] == 7
    # Bob owns nothing: his aggregates are all zero.
    assert bob_overview["raffles"]["total"] == 0
    assert bob_overview["tickets"]["total"] == 0
    assert bob_overview["participants"] == 0
