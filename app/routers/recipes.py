"""Recipes router for browsing and managing recipes."""

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import RecipeCreate, RecipeRead, RecipeSummary
from app.services.ingredient import get_ingredient_by_id
from app.services.recipe import (
    create_recipe,
    get_recipe_by_id,
    get_recipes,
    search_recipes,
)
from app.utils.dependencies import DbSession

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get(
    "/",
    response_model=list[RecipeSummary],
    summary="List all recipes",
    responses={
        200: {"description": "List of recipes"},
    },
)
async def list_recipes(
    db: DbSession,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
    difficulty: str | None = Query(
        None,
        pattern="^(easy|medium|hard)$",
        description="Filter by difficulty level",
    ),
    max_prep_time: int | None = Query(
        None, ge=0, description="Maximum prep time in minutes"
    ),
    max_cook_time: int | None = Query(
        None, ge=0, description="Maximum cook time in minutes"
    ),
) -> list[RecipeSummary]:
    """Get a paginated list of all recipes.

    Filter options:
    - **difficulty**: Filter by difficulty level (easy, medium, hard)
    - **max_prep_time**: Maximum prep time in minutes
    - **max_cook_time**: Maximum cook time in minutes

    Use `skip` and `limit` for pagination.
    """
    recipes = await get_recipes(
        db,
        skip=skip,
        limit=limit,
        difficulty=difficulty,
        max_prep_time=max_prep_time,
        max_cook_time=max_cook_time,
    )
    return [RecipeSummary.model_validate(recipe) for recipe in recipes]


@router.get(
    "/search",
    response_model=list[RecipeSummary],
    summary="Search recipes",
    responses={
        200: {"description": "Search results"},
    },
)
async def search_recipes_endpoint(
    db: DbSession,
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
) -> list[RecipeSummary]:
    """Search recipes by title or description.

    Performs a case-insensitive partial match on recipe titles and descriptions.
    """
    recipes = await search_recipes(db, query_text=q, skip=skip, limit=limit)
    return [RecipeSummary.model_validate(recipe) for recipe in recipes]


@router.get(
    "/{recipe_id}",
    response_model=RecipeRead,
    summary="Get recipe details",
    responses={
        200: {"description": "Full recipe details with ingredients"},
        404: {"description": "Recipe not found"},
    },
)
async def get_recipe(recipe_id: int, db: DbSession) -> RecipeRead:
    """Get full details for a single recipe, including all ingredients.

    Returns:
    - Recipe metadata (title, description, times, difficulty, etc.)
    - Complete ingredient list with quantities and units
    - Step-by-step instructions
    """
    recipe = await get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with ID {recipe_id} not found",
        )
    return RecipeRead.model_validate(recipe)


@router.post(
    "/",
    response_model=RecipeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recipe",
    responses={
        201: {"description": "Recipe created successfully"},
        400: {"description": "Invalid ingredient(s)"},
    },
)
async def create_new_recipe(
    recipe_data: RecipeCreate,
    db: DbSession,
) -> RecipeRead:
    """Create a new recipe with ingredients.

    **Recipe fields:**
    - **title**: Recipe name (required)
    - **description**: Brief description
    - **instructions**: Step-by-step cooking instructions (required)
    - **prep_time**: Preparation time in minutes
    - **cook_time**: Cooking time in minutes
    - **difficulty_level**: easy, medium, or hard
    - **servings**: Number of servings
    - **image_url**: URL to recipe image
    - **source_url**: URL to original recipe source

    **Ingredients list:**
    Each ingredient requires:
    - **ingredient_id**: ID of an existing ingredient
    - **quantity**: Amount needed (e.g., "2", "1/2")
    - **unit**: Unit of measurement (e.g., "cups", "tbsp")
    - **optional**: Whether the ingredient is optional (default: false)

    Note: In a production system, this endpoint would typically be restricted
    to admin users only.
    """
    # Validate all ingredient IDs exist
    for ing_data in recipe_data.ingredients:
        ingredient = await get_ingredient_by_id(db, ing_data.ingredient_id)
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ingredient with ID {ing_data.ingredient_id} not found",
            )

    recipe = await create_recipe(db, recipe_data)
    return RecipeRead.model_validate(recipe)
