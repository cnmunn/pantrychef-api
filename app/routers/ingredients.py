"""Ingredients router for managing recipe components."""

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import IngredientCreate, IngredientRead
from app.services.ingredient import (
    create_ingredient,
    get_all_categories,
    get_ingredient_by_id,
    get_ingredient_by_name,
    get_ingredients,
)
from app.utils.dependencies import DbSession

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


@router.get(
    "/",
    response_model=list[IngredientRead],
    summary="List all ingredients",
    responses={
        200: {"description": "List of ingredients"},
    },
)
async def list_ingredients(
    db: DbSession,
    category: str | None = Query(
        None,
        description="Filter ingredients by category (e.g., produce, dairy, protein)",
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
) -> list[IngredientRead]:
    """Get a paginated list of all ingredients.

    Optionally filter by category to narrow down results. Categories include:
    - **produce**: Fresh fruits and vegetables
    - **dairy**: Milk, cheese, yogurt, etc.
    - **protein**: Meat, poultry, fish, tofu, etc.
    - **grains**: Rice, pasta, bread, etc.
    - **spices**: Herbs and seasonings
    - **pantry**: Canned goods, oils, condiments

    Use `skip` and `limit` for pagination.
    """
    ingredients = await get_ingredients(db, category=category, skip=skip, limit=limit)
    return [IngredientRead.model_validate(ing) for ing in ingredients]


@router.get(
    "/categories",
    response_model=list[str],
    summary="List all ingredient categories",
    responses={
        200: {"description": "List of unique category names"},
    },
)
async def list_categories(db: DbSession) -> list[str]:
    """Get all unique ingredient categories.

    Returns a sorted list of all category names currently in use.
    Useful for populating filter dropdowns in the UI.
    """
    return await get_all_categories(db)


@router.get(
    "/{ingredient_id}",
    response_model=IngredientRead,
    summary="Get ingredient by ID",
    responses={
        200: {"description": "Ingredient details"},
        404: {"description": "Ingredient not found"},
    },
)
async def get_ingredient(ingredient_id: int, db: DbSession) -> IngredientRead:
    """Get a single ingredient by its ID.

    Returns the full details of the specified ingredient.
    """
    ingredient = await get_ingredient_by_id(db, ingredient_id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with ID {ingredient_id} not found",
        )
    return IngredientRead.model_validate(ingredient)


@router.post(
    "/",
    response_model=IngredientRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ingredient",
    responses={
        201: {"description": "Ingredient created successfully"},
        400: {"description": "Ingredient with this name already exists"},
    },
)
async def create_new_ingredient(
    ingredient_data: IngredientCreate,
    db: DbSession,
) -> IngredientRead:
    """Create a new ingredient.

    Adds a new ingredient to the database. The ingredient name must be unique.

    - **name**: Unique ingredient name (1-100 characters)
    - **category**: Category classification (e.g., produce, dairy, protein)

    Note: In a production system, this endpoint would typically be restricted
    to admin users only.
    """
    # Check if ingredient with this name already exists
    existing = await get_ingredient_by_name(db, ingredient_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient '{ingredient_data.name}' already exists",
        )

    ingredient = await create_ingredient(db, ingredient_data)
    return IngredientRead.model_validate(ingredient)
