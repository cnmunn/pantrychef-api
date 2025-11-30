"""Favorites router for managing user's saved recipes."""

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import FavoriteRead, Message
from app.services.favorite import (
    add_favorite,
    get_favorite_by_recipe,
    get_user_favorites,
    remove_favorite,
)
from app.services.recipe import get_recipe_by_id
from app.utils.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get(
    "/",
    response_model=list[FavoriteRead],
    summary="List favorite recipes",
    responses={
        200: {"description": "List of favorite recipes"},
        401: {"description": "Not authenticated"},
    },
)
async def list_favorites(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum records to return"),
) -> list[FavoriteRead]:
    """Get all recipes saved to your favorites.

    Returns favorites sorted by most recently added, with recipe summary details.
    Use `skip` and `limit` for pagination.
    """
    favorites = await get_user_favorites(db, current_user.id, skip=skip, limit=limit)
    return [FavoriteRead.model_validate(fav) for fav in favorites]


@router.post(
    "/{recipe_id}",
    response_model=FavoriteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add recipe to favorites",
    responses={
        201: {"description": "Recipe added to favorites"},
        400: {"description": "Recipe already in favorites or not found"},
        401: {"description": "Not authenticated"},
    },
)
async def add_to_favorites(
    recipe_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> FavoriteRead:
    """Add a recipe to your favorites.

    Each recipe can only be favorited once per user.
    """
    # Verify recipe exists
    recipe = await get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recipe with ID {recipe_id} not found",
        )

    # Check if already favorited
    existing = await get_favorite_by_recipe(db, current_user.id, recipe_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recipe is already in your favorites",
        )

    favorite = await add_favorite(db, current_user.id, recipe_id)
    return FavoriteRead.model_validate(favorite)


@router.delete(
    "/{recipe_id}",
    response_model=Message,
    summary="Remove recipe from favorites",
    responses={
        200: {"description": "Recipe removed from favorites"},
        401: {"description": "Not authenticated"},
        404: {"description": "Recipe not in favorites"},
    },
)
async def remove_from_favorites(
    recipe_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Message:
    """Remove a recipe from your favorites."""
    removed = await remove_favorite(db, current_user.id, recipe_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe is not in your favorites",
        )
    return Message(message="Recipe removed from favorites")
