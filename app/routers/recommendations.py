"""Recommendations router for recipe matching based on pantry ingredients."""

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import RecipeMatch, ShoppingList
from app.services.recommendation import get_recipe_recommendations, get_shopping_list
from app.utils.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get(
    "/",
    response_model=list[RecipeMatch],
    summary="Get recipe recommendations",
    responses={
        200: {"description": "Recipes ranked by pantry match"},
        401: {"description": "Not authenticated"},
    },
)
async def get_recommendations(
    db: DbSession,
    current_user: CurrentUser,
    min_match_percent: float = Query(
        0.0,
        ge=0,
        le=100,
        description="Minimum ingredient match percentage (0-100)",
    ),
    max_missing_ingredients: int | None = Query(
        None,
        ge=0,
        description="Maximum number of missing ingredients allowed",
    ),
    difficulty: str | None = Query(
        None,
        pattern="^(easy|medium|hard)$",
        description="Filter by difficulty level",
    ),
    max_total_time: int | None = Query(
        None,
        ge=0,
        description="Maximum total time (prep + cook) in minutes",
    ),
    vegetarian: bool = Query(
        False,
        description="Only include vegetarian recipes (no meat, poultry, fish)",
    ),
    vegan: bool = Query(
        False,
        description="Only include vegan recipes (no animal products)",
    ),
    gluten_free: bool = Query(
        False,
        description="Only include gluten-free recipes",
    ),
    exclude_allergens: list[str] = Query(
        default=[],
        description="Allergens to exclude (e.g., dairy, nuts, shellfish, eggs, soy, wheat)",
    ),
    prioritize_expiring: bool = Query(
        False,
        description="Prioritize recipes using ingredients expiring soon",
    ),
    limit: int = Query(20, ge=1, le=100, description="Maximum recipes to return"),
) -> list[RecipeMatch]:
    """**Core Feature**: Get personalized recipe recommendations based on your pantry.

    This endpoint analyzes your pantry inventory and returns recipes ranked by
    how many required ingredients you already have.

    **How matching works:**
    - Only **required** ingredients (non-optional) are considered for match percentage
    - Recipes are sorted by match percentage (highest first)
    - Each recipe shows which ingredients you have and which you're missing

    **Filtering options:**
    - **min_match_percent**: Only show recipes where you have at least X% of ingredients
    - **max_missing_ingredients**: Only show recipes missing at most N ingredients
    - **difficulty**: Filter by easy, medium, or hard recipes
    - **max_total_time**: Filter by maximum prep + cook time

    **Dietary filters:**
    - **vegetarian**: Exclude recipes with meat, poultry, or fish
    - **vegan**: Exclude recipes with any animal products
    - **gluten_free**: Exclude recipes with gluten-containing ingredients
    - **exclude_allergens**: Exclude recipes containing specific allergens

    **Smart features:**
    - **prioritize_expiring**: Sort by recipes that use soon-to-expire ingredients first

    **Example use cases:**
    - Set `min_match_percent=100` to see recipes you can make right now
    - Set `max_missing_ingredients=2` to see recipes needing just a few more items
    - Use `vegetarian=true&exclude_allergens=nuts` for nut-free vegetarian meals
    - Use `prioritize_expiring=true` to reduce food waste

    **Response includes:**
    - Recipe summary information
    - `match_percentage`: What % of required ingredients you have
    - `matched_ingredients`: Count of matched ingredients
    - `total_required_ingredients`: Total required ingredients in recipe
    - `missing_ingredients`: List of ingredients you need to buy
    - `uses_expiring_ingredients`: Count of expiring items used (when prioritize_expiring=true)
    """
    matches = await get_recipe_recommendations(
        db,
        user_id=current_user.id,
        min_match_percent=min_match_percent,
        max_missing_ingredients=max_missing_ingredients,
        difficulty=difficulty,
        max_total_time=max_total_time,
        vegetarian=vegetarian,
        vegan=vegan,
        gluten_free=gluten_free,
        exclude_allergens=exclude_allergens if exclude_allergens else None,
        prioritize_expiring=prioritize_expiring,
        limit=limit,
    )
    return matches


@router.get(
    "/{recipe_id}/shopping-list",
    response_model=ShoppingList,
    summary="Get shopping list for a recipe",
    responses={
        200: {"description": "Shopping list with missing ingredients"},
        401: {"description": "Not authenticated"},
        404: {"description": "Recipe not found"},
    },
)
async def get_recipe_shopping_list(
    recipe_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> ShoppingList:
    """Generate a shopping list for a specific recipe.

    Compares the recipe's ingredients against your pantry and returns
    a list of items you need to buy.

    **Includes:**
    - All missing ingredients (both required and optional)
    - Quantities and units needed
    - Total count of missing items

    Use this to plan your grocery shopping for a specific recipe.
    """
    shopping_list = await get_shopping_list(db, current_user.id, recipe_id)
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found",
        )
    return shopping_list
