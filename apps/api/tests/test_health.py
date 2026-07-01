from httpx import AsyncClient


async def test_health_check_returns_success_envelope(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "success": True,
        "message": "API is running.",
        "data": {"status": "ok"},
    }
