from fastapi import APIRouter

from app.modules.analytics.routers import router as analytics_router
from app.modules.collaborators.routers import router as collaborators_router
from app.modules.dashboard.routers import router as dashboard_router
from app.modules.participants.routers import router as participants_router
from app.modules.public.routers import router as public_router
from app.modules.raffles.routers import router as raffles_router
from app.modules.tickets.routers import router as tickets_router
from app.modules.users.routers import router as users_router

api_router = APIRouter()

# Authentication (public: register/login; me/logout use the session cookie).
api_router.include_router(users_router, prefix="/auth", tags=["auth"])

# Business modules register their routers here (owner-scoped, require auth).
api_router.include_router(raffles_router, prefix="/raffles", tags=["raffles"])
api_router.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
api_router.include_router(participants_router, prefix="/participants", tags=["participants"])
api_router.include_router(collaborators_router, prefix="/collaborators", tags=["collaborators"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

# Public, unauthenticated portal (separate surface from the admin modules).
api_router.include_router(public_router, prefix="/public", tags=["public"])
