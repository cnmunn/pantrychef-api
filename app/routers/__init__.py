"""API routers for different resource endpoints."""

from app.routers.auth import router as auth_router
from app.routers.favorites import router as favorites_router
from app.routers.history import router as history_router
from app.routers.ingredients import router as ingredients_router
from app.routers.pantry import router as pantry_router
from app.routers.recipes import router as recipes_router
from app.routers.recommendations import router as recommendations_router

__all__ = [
    "auth_router",
    "favorites_router",
    "history_router",
    "ingredients_router",
    "pantry_router",
    "recipes_router",
    "recommendations_router",
]
