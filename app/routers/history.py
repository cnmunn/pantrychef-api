"""Cooking history router for tracking cooked recipes."""

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import CookingHistoryCreate, CookingHistoryRead, CookingStats
from app.services.cooking_history import (
    get_cooking_stats,
    get_user_cooking_history,
    log_cooked_recipe,
)
from app.services.recipe import get_recipe_by_id
from app.utils.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/history", tags=["Cooking History"])


@router.get(
    "/",
    response_model=list[CookingHistoryRead],
    summary="List cooking history",
    responses={
        200: {"description": "Cooking history entries"},
        401: {"description": "Not authenticated"},
    },
)
async def list_cooking_history(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
) -> list[CookingHistoryRead]:
    """Get your cooking history.

    Returns a log of all recipes you've cooked, sorted by most recent first.
    Each entry includes the recipe details, when you cooked it, your rating, and notes.

    Use `skip` and `limit` for pagination.
    """
    history = await get_user_cooking_history(db, current_user.id, skip=skip, limit=limit)
    return [CookingHistoryRead.model_validate(entry) for entry in history]


@router.get(
    "/stats",
    response_model=CookingStats,
    summary="Get cooking statistics",
    responses={
        200: {"description": "Cooking statistics"},
        401: {"description": "Not authenticated"},
    },
)
async def get_stats(
    db: DbSession,
    current_user: CurrentUser,
) -> CookingStats:
    """Get your cooking statistics.

    **Statistics include:**
    - **total_recipes_cooked**: Total number of times you've cooked (including repeats)
    - **unique_recipes_cooked**: Number of different recipes you've tried
    - **average_rating**: Your average rating across all rated meals
    - **most_cooked_recipe**: The recipe you've made most often
    - **most_cooked_count**: How many times you've made your most cooked recipe
    """
    return await get_cooking_stats(db, current_user.id)


@router.post(
    "/",
    response_model=CookingHistoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log a cooked recipe",
    responses={
        201: {"description": "Recipe logged successfully"},
        400: {"description": "Recipe not found"},
        401: {"description": "Not authenticated"},
    },
)
async def log_recipe(
    entry_data: CookingHistoryCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> CookingHistoryRead:
    """Log that you've cooked a recipe.

    Track your cooking journey by logging recipes when you make them.
    You can log the same recipe multiple times.

    - **recipe_id**: ID of the recipe you cooked (required)
    - **rating**: Your rating from 1-5 stars (optional)
    - **notes**: Personal notes about this cooking session (optional)

    **Tips for notes:**
    - What modifications did you make?
    - How did it turn out?
    - What would you do differently next time?
    """
    # Verify recipe exists
    recipe = await get_recipe_by_id(db, entry_data.recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recipe with ID {entry_data.recipe_id} not found",
        )

    entry = await log_cooked_recipe(db, current_user.id, entry_data)
    return CookingHistoryRead.model_validate(entry)
