"""FastAPI application entry point."""

from fastapi import FastAPI

from app.config import get_settings
from app.routers import (
    auth_router,
    favorites_router,
    history_router,
    ingredients_router,
    pantry_router,
    recipes_router,
    recommendations_router,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=(
        "A recipe recommendation service that suggests meals based on ingredients you have at home"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Include routers
app.include_router(auth_router)
app.include_router(ingredients_router)
app.include_router(pantry_router)
app.include_router(recipes_router)
app.include_router(recommendations_router)
app.include_router(favorites_router)
app.include_router(history_router)


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """Root endpoint returning API info."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
