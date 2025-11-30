"""API routers for different resource endpoints."""

from app.routers.auth import router as auth_router

__all__ = [
    "auth_router",
]
