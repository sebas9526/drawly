from fastapi import APIRouter

from app.core.responses import SuccessResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=SuccessResponse[dict[str, str]])
async def health_check() -> SuccessResponse[dict[str, str]]:
    """Unversioned infra health check, used by Docker/orchestrator probes."""
    return SuccessResponse(message="API is running.", data={"status": "ok"})
