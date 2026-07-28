"""CORS wiring — mirrors exactly how app/main.py configures CORSMiddleware
(allow_origins + allow_origin_regex together), constructed standalone here
rather than against the shared app.main.app instance since that singleton is
built once at import time from whatever env vars were set then (see
tests/conftest.py and tests/core/test_rate_limit.py for the same constraint).

Regression: a production login failure traced to Vercel giving every
deployment (including production) its own unique URL in addition to the
custom domain — only the custom domain was in BACKEND_CORS_ORIGINS, so the
preflight from the deployment URL got Starlette's 400 "disallowed CORS
origin". allow_origin_regex covers any of an account's Vercel deployment/
preview URLs without an env var edit on every deploy.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import ASGITransport, AsyncClient, Response

_ALLOWED_EXACT = ["https://drawly-web-pi.vercel.app"]
_ALLOWED_REGEX = r"^https://drawly[a-z0-9-]*-sebas952601s-projects\.vercel\.app$"


def _build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_ALLOWED_EXACT,
        allow_origin_regex=_ALLOWED_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/ping")
    async def ping() -> dict[str, bool]:
        return {"ok": True}

    return app


async def _preflight(origin: str) -> Response:
    transport = ASGITransport(app=_build_app())
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.options(
            "/ping",
            headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
        )


async def test_exact_listed_origin_is_allowed() -> None:
    response = await _preflight("https://drawly-web-pi.vercel.app")
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://drawly-web-pi.vercel.app"


async def test_vercel_deployment_url_is_allowed_via_regex() -> None:
    origin = "https://drawly-d2wnu1xml-sebas952601s-projects.vercel.app"
    response = await _preflight(origin)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


async def test_vercel_preview_branch_url_is_allowed_via_regex() -> None:
    origin = "https://drawly-web-git-feature-x-sebas952601s-projects.vercel.app"
    response = await _preflight(origin)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


async def test_unrelated_origin_is_still_rejected() -> None:
    response = await _preflight("https://evil.example.com")
    assert response.status_code == 400
