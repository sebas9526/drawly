from fastapi import APIRouter

api_router = APIRouter()

# Business modules register their routers here, e.g.:
# from app.modules.raffles.routers import router as raffles_router
# api_router.include_router(raffles_router, prefix="/raffles", tags=["raffles"])
