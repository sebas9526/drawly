"""End-to-end API tests for collaborators (SQLite-backed).

Covers CRUD, activate/deactivate, per-raffle listing and stats, crediting a
collaborator on a reservation (admin + public), and cross-user ownership.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from httpx import AsyncClient

API = "/api/v1"

ClientFactory = Callable[[str], Awaitable[AsyncClient]]


async def _create_raffle(client: AsyncClient, *, total: int = 5, title: str = "Rifa") -> str:
    response = await client.post(
        f"{API}/raffles",
        json={
            "title": title,
            "description": "d",
            "prize": "p",
            "ticket_price": 1000,
            "total_tickets": total,
            "draw_date": "2026-08-01T19:00:00+00:00",
        },
    )
    assert response.status_code == 201, response.text
    return str(response.json()["data"]["id"])


async def _create_collaborator(
    client: AsyncClient, raffle_id: str, *, name: str = "Juan", is_active: bool = True
) -> dict[str, Any]:
    return await _create_collaborator_for(client, [raffle_id], name=name, is_active=is_active)


async def _create_collaborator_for(
    client: AsyncClient, raffle_ids: list[str], *, name: str = "Juan", is_active: bool = True
) -> dict[str, Any]:
    response = await client.post(
        f"{API}/collaborators",
        json={"raffle_ids": raffle_ids, "name": name, "color": "#4F46E5", "is_active": is_active},
    )
    assert response.status_code == 201, response.text
    data: dict[str, Any] = response.json()["data"]
    return data


async def test_collaborator_crud(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client)
    created = await _create_collaborator(api_client, raffle_id, name="Juan")
    assert created["name"] == "Juan"
    assert created["is_active"] is True
    cid = created["id"]

    # Update
    updated = await api_client.put(
        f"{API}/collaborators/{cid}", json={"name": "Juan Pérez", "color": "#EF4444"}
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["name"] == "Juan Pérez"
    assert updated.json()["data"]["color"] == "#EF4444"

    # Deactivate / activate
    deactivated = await api_client.patch(f"{API}/collaborators/{cid}/deactivate")
    assert deactivated.json()["data"]["is_active"] is False
    activated = await api_client.patch(f"{API}/collaborators/{cid}/activate")
    assert activated.json()["data"]["is_active"] is True

    # List + by raffle
    listed = await api_client.get(f"{API}/collaborators", params={"raffle_id": raffle_id})
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1
    by_raffle = await api_client.get(f"{API}/collaborators/raffle/{raffle_id}")
    assert len(by_raffle.json()["data"]) == 1

    # Delete (soft)
    deleted = await api_client.delete(f"{API}/collaborators/{cid}")
    assert deleted.status_code == 200
    gone = await api_client.get(f"{API}/collaborators/{cid}")
    assert gone.status_code == 404


async def test_create_collaborator_requires_owned_raffle(
    client_factory: ClientFactory,
) -> None:
    alice = await client_factory("alice@drawly.test")
    bob = await client_factory("bob@drawly.test")
    alice_raffle = await _create_raffle(alice)

    # Bob cannot create a collaborator on Alice's raffle.
    response = await bob.post(
        f"{API}/collaborators",
        json={"raffle_ids": [alice_raffle], "name": "Intruso", "color": "#4F46E5"},
    )
    assert response.status_code == 404


async def test_collaborators_isolated_per_user(client_factory: ClientFactory) -> None:
    alice = await client_factory("alice@drawly.test")
    bob = await client_factory("bob@drawly.test")
    raffle_id = await _create_raffle(alice)
    collaborator = await _create_collaborator(alice, raffle_id)

    # Bob sees nothing and cannot fetch Alice's collaborator.
    assert (await bob.get(f"{API}/collaborators")).json()["data"] == []
    assert (await bob.get(f"{API}/collaborators/{collaborator['id']}")).status_code == 404


async def test_reserve_credits_collaborator_and_validates_raffle(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client, total=3)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    collaborator = await _create_collaborator(api_client, raffle_id)

    tickets = (await api_client.get(f"{API}/tickets", params={"raffle_id": raffle_id})).json()[
        "data"
    ]
    ticket_id = tickets[0]["id"]

    reserved = await api_client.patch(
        f"{API}/tickets/{ticket_id}/reserve", json={"collaborator_id": collaborator["id"]}
    )
    assert reserved.status_code == 200, reserved.text
    assert reserved.json()["data"]["collaborator_id"] == collaborator["id"]

    # A collaborator from a different raffle is rejected.
    other_raffle = await _create_raffle(api_client, total=3, title="Otra")
    other_collab = await _create_collaborator(api_client, other_raffle, name="Ana")
    ticket2 = tickets[1]["id"]
    bad = await api_client.patch(
        f"{API}/tickets/{ticket2}/reserve", json={"collaborator_id": other_collab["id"]}
    )
    assert bad.status_code == 404


async def test_collaborator_stats(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client, total=4)
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    collaborator = await _create_collaborator(api_client, raffle_id)
    cid = collaborator["id"]

    tickets = (await api_client.get(f"{API}/tickets", params={"raffle_id": raffle_id})).json()[
        "data"
    ]
    # Reserve two tickets for the collaborator; pay one of them.
    await api_client.patch(
        f"{API}/tickets/{tickets[0]['id']}/reserve", json={"collaborator_id": cid}
    )
    await api_client.patch(
        f"{API}/tickets/{tickets[1]['id']}/reserve", json={"collaborator_id": cid}
    )
    await api_client.patch(f"{API}/tickets/{tickets[1]['id']}/pay")

    stats = await api_client.get(f"{API}/collaborators/raffle/{raffle_id}/stats")
    assert stats.status_code == 200, stats.text
    row = next(r for r in stats.json()["data"] if r["collaborator_id"] == cid)
    assert row["reserved"] == 1  # still reserved (pending)
    assert row["paid"] == 1
    assert row["total"] == 2
    assert row["total_value"] == 2000.0  # 2 tickets * 1000


async def test_public_reserve_with_collaborator(api_client: AsyncClient) -> None:
    raffle_id = await _create_raffle(api_client, total=3, title="Pública")
    await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
    collaborator = await _create_collaborator(api_client, raffle_id, name="Vendedor")
    # Publish so the public portal can see it.
    published = await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
    slug = published.json()["data"]["public_slug"]

    # Public sees the active collaborator.
    public_collabs = await api_client.get(f"{API}/public/raffles/{slug}/collaborators")
    assert public_collabs.status_code == 200
    assert [c["name"] for c in public_collabs.json()["data"]] == ["Vendedor"]

    # Public reserve crediting the collaborator succeeds.
    reserve = await api_client.post(
        f"{API}/public/raffles/{slug}/reserve",
        json={
            "ticket_number": 1,
            "participant": {"full_name": "Cliente", "phone": "3000000000"},
            "collaborator_id": collaborator["id"],
        },
    )
    assert reserve.status_code == 201, reserve.text


async def test_same_collaborator_can_sell_for_two_raffles(api_client: AsyncClient) -> None:
    raffle_a = await _create_raffle(api_client, total=2, title="Rifa A")
    raffle_b = await _create_raffle(api_client, total=2, title="Rifa B")
    collaborator = await _create_collaborator_for(api_client, [raffle_a, raffle_b], name="Ana")
    assert sorted(collaborator["raffle_ids"]) == sorted([raffle_a, raffle_b])

    by_a = await api_client.get(f"{API}/collaborators/raffle/{raffle_a}")
    by_b = await api_client.get(f"{API}/collaborators/raffle/{raffle_b}")
    assert [c["id"] for c in by_a.json()["data"]] == [collaborator["id"]]
    assert [c["id"] for c in by_b.json()["data"]] == [collaborator["id"]]

    # Reservations in either raffle can credit the same collaborator.
    for raffle_id in (raffle_a, raffle_b):
        await api_client.post(f"{API}/raffles/{raffle_id}/tickets")
        await api_client.patch(f"{API}/raffles/{raffle_id}/publish")
        tickets = (await api_client.get(f"{API}/tickets", params={"raffle_id": raffle_id})).json()[
            "data"
        ]
        reserved = await api_client.patch(
            f"{API}/tickets/{tickets[0]['id']}/reserve",
            json={"collaborator_id": collaborator["id"]},
        )
        assert reserved.status_code == 200, reserved.text


async def test_editing_raffle_ids_replaces_the_whole_set(api_client: AsyncClient) -> None:
    raffle_a = await _create_raffle(api_client, total=2, title="Rifa A")
    raffle_b = await _create_raffle(api_client, total=2, title="Rifa B")
    collaborator = await _create_collaborator_for(api_client, [raffle_a], name="Ana")

    updated = await api_client.put(
        f"{API}/collaborators/{collaborator['id']}", json={"raffle_ids": [raffle_b]}
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["raffle_ids"] == [raffle_b]

    by_a = await api_client.get(f"{API}/collaborators/raffle/{raffle_a}")
    by_b = await api_client.get(f"{API}/collaborators/raffle/{raffle_b}")
    assert by_a.json()["data"] == []
    assert [c["id"] for c in by_b.json()["data"]] == [collaborator["id"]]


async def test_set_collaborators_for_raffle_replaces_the_whole_set(api_client: AsyncClient) -> None:
    """Driven from the raffle form: PUT /collaborators/raffle/{id} replaces
    who sells that raffle without touching a collaborator's other raffles."""
    raffle = await _create_raffle(api_client, title="Rifa")
    other_raffle = await _create_raffle(api_client, title="Otra rifa")
    ana = await _create_collaborator_for(api_client, [raffle, other_raffle], name="Ana")
    beto = await _create_collaborator_for(api_client, [raffle], name="Beto")
    caro = await _create_collaborator_for(api_client, [other_raffle], name="Caro")

    response = await api_client.put(
        f"{API}/collaborators/raffle/{raffle}",
        json={"collaborator_ids": [beto["id"], caro["id"]]},
    )
    assert response.status_code == 200, response.text
    assert sorted(c["id"] for c in response.json()["data"]) == sorted([beto["id"], caro["id"]])

    by_raffle = await api_client.get(f"{API}/collaborators/raffle/{raffle}")
    assert sorted(c["id"] for c in by_raffle.json()["data"]) == sorted([beto["id"], caro["id"]])

    # Ana was dropped from `raffle` but keeps her link to `other_raffle`.
    ana_after = await api_client.get(f"{API}/collaborators/{ana['id']}")
    assert ana_after.json()["data"]["raffle_ids"] == [other_raffle]


async def test_set_collaborators_for_raffle_accepts_empty_list(api_client: AsyncClient) -> None:
    raffle = await _create_raffle(api_client)
    collaborator = await _create_collaborator(api_client, raffle)

    response = await api_client.put(
        f"{API}/collaborators/raffle/{raffle}", json={"collaborator_ids": []}
    )
    assert response.status_code == 200, response.text
    assert response.json()["data"] == []

    by_raffle = await api_client.get(f"{API}/collaborators/raffle/{raffle}")
    assert by_raffle.json()["data"] == []
    # The collaborator itself still exists, just unlinked from this raffle.
    still_there = await api_client.get(f"{API}/collaborators/{collaborator['id']}")
    assert still_there.status_code == 200
    assert still_there.json()["data"]["raffle_ids"] == []


async def test_set_collaborators_for_raffle_rejects_unowned_raffle(
    client_factory: ClientFactory,
) -> None:
    alice = await client_factory("alice@drawly.test")
    bob = await client_factory("bob@drawly.test")
    alice_raffle = await _create_raffle(alice)

    response = await bob.put(
        f"{API}/collaborators/raffle/{alice_raffle}", json={"collaborator_ids": []}
    )
    assert response.status_code == 404


async def test_set_collaborators_for_raffle_rejects_unowned_collaborator(
    client_factory: ClientFactory,
) -> None:
    alice = await client_factory("alice@drawly.test")
    bob = await client_factory("bob@drawly.test")
    alice_raffle = await _create_raffle(alice)
    bob_raffle = await _create_raffle(bob)
    bob_collaborator = await _create_collaborator(bob, bob_raffle, name="Intruso")

    response = await alice.put(
        f"{API}/collaborators/raffle/{alice_raffle}",
        json={"collaborator_ids": [bob_collaborator["id"]]},
    )
    assert response.status_code == 404

    # Nothing was linked — the raffle still has zero collaborators.
    by_raffle = await alice.get(f"{API}/collaborators/raffle/{alice_raffle}")
    assert by_raffle.json()["data"] == []
