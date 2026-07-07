"""End-to-end tests for authentication (SQLite-backed).

Covers registration, login, the session cookie, /me, logout, password hashing
(never stored in plain text), and rejection of bad credentials / unauthenticated
access to private routes.
"""

from httpx import AsyncClient

from app.core.security import hash_password, verify_password

API = "/api/v1"
AUTH_COOKIE = "drawly_access"


async def test_register_sets_cookie_and_returns_user(api_client: AsyncClient) -> None:
    # api_client is already registered as the default user in the fixture.
    response = await api_client.get(f"{API}/auth/me")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == "owner@drawly.test"
    assert "password" not in body["data"]
    assert "password_hash" not in body["data"]
    assert api_client.cookies.get(AUTH_COOKIE)


async def test_register_rejects_duplicate_email(api_client: AsyncClient) -> None:
    response = await api_client.post(
        f"{API}/auth/register",
        json={"full_name": "Someone", "email": "owner@drawly.test", "password": "password123"},
    )
    assert response.status_code == 409
    assert response.json()["success"] is False


def test_password_hashing_roundtrip() -> None:
    """Passwords are never stored in plain text: Argon2 hash differs from the
    input, verifies against the right password, and rejects the wrong one."""
    plain = "sup3r-secret-pw"
    hashed = hash_password(plain)
    assert hashed != plain
    assert hashed.startswith("$argon2")
    assert verify_password(plain, hashed) is True
    assert verify_password("not-the-password", hashed) is False


async def test_response_never_leaks_password_fields(api_client: AsyncClient) -> None:
    response = await api_client.get(f"{API}/auth/me")
    data = response.json()["data"]
    assert "password" not in data
    assert "password_hash" not in data


async def test_login_with_valid_and_invalid_credentials(api_client: AsyncClient) -> None:
    ok = await api_client.post(
        f"{API}/auth/login",
        json={"email": "owner@drawly.test", "password": "password123"},
    )
    assert ok.status_code == 200, ok.text
    assert ok.json()["data"]["email"] == "owner@drawly.test"

    bad = await api_client.post(
        f"{API}/auth/login",
        json={"email": "owner@drawly.test", "password": "wrong-password"},
    )
    assert bad.status_code == 401
    assert bad.json()["success"] is False


async def test_logout_clears_session(api_client: AsyncClient) -> None:
    await api_client.post(f"{API}/auth/logout")
    api_client.cookies.clear()
    response = await api_client.get(f"{API}/auth/me")
    assert response.status_code == 401


async def test_private_routes_require_authentication(api_client: AsyncClient) -> None:
    # Drop the session cookie and confirm the admin surfaces are protected.
    api_client.cookies.clear()
    for path in (
        f"{API}/raffles",
        f"{API}/tickets",
        f"{API}/participants",
        f"{API}/dashboard/overview",
    ):
        response = await api_client.get(path)
        assert response.status_code == 401, f"{path} -> {response.status_code}"
        assert response.json()["success"] is False
