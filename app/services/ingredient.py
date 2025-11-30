"""Ingredient service for database operations."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingredient import Ingredient
from app.schemas.ingredient import IngredientCreate


async def get_ingredient_by_id(db: AsyncSession, ingredient_id: int) -> Ingredient | None:
    """Get an ingredient by its ID.

    Args:
        db: Database session.
        ingredient_id: Ingredient ID to look up.

    Returns:
        Ingredient object if found, None otherwise.
    """
    result = await db.execute(select(Ingredient).where(Ingredient.id == ingredient_id))
    return result.scalar_one_or_none()


async def get_ingredient_by_name(db: AsyncSession, name: str) -> Ingredient | None:
    """Get an ingredient by its name (case-insensitive).

    Args:
        db: Database session.
        name: Ingredient name to look up.

    Returns:
        Ingredient object if found, None otherwise.
    """
    result = await db.execute(
        select(Ingredient).where(func.lower(Ingredient.name) == name.lower())
    )
    return result.scalar_one_or_none()


async def get_ingredients(
    db: AsyncSession,
    category: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Ingredient]:
    """Get a list of ingredients with optional category filter.

    Args:
        db: Database session.
        category: Optional category to filter by.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.

    Returns:
        List of Ingredient objects.
    """
    query = select(Ingredient).order_by(Ingredient.name)

    if category:
        query = query.where(func.lower(Ingredient.category) == category.lower())

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_all_categories(db: AsyncSession) -> list[str]:
    """Get all unique ingredient categories.

    Args:
        db: Database session.

    Returns:
        List of unique category names, sorted alphabetically.
    """
    result = await db.execute(
        select(Ingredient.category).distinct().order_by(Ingredient.category)
    )
    return list(result.scalars().all())


async def create_ingredient(db: AsyncSession, ingredient_data: IngredientCreate) -> Ingredient:
    """Create a new ingredient in the database.

    Args:
        db: Database session.
        ingredient_data: Ingredient creation data.

    Returns:
        Created Ingredient object.
    """
    ingredient = Ingredient(
        name=ingredient_data.name,
        category=ingredient_data.category,
        is_vegetarian=ingredient_data.is_vegetarian,
        is_vegan=ingredient_data.is_vegan,
        is_gluten_free=ingredient_data.is_gluten_free,
        allergens=ingredient_data.allergens,
    )

    db.add(ingredient)
    await db.flush()
    await db.refresh(ingredient)

    return ingredient


async def count_ingredients(db: AsyncSession, category: str | None = None) -> int:
    """Count total number of ingredients, optionally filtered by category.

    Args:
        db: Database session.
        category: Optional category to filter by.

    Returns:
        Total count of ingredients.
    """
    query = select(func.count(Ingredient.id))

    if category:
        query = query.where(func.lower(Ingredient.category) == category.lower())

    result = await db.execute(query)
    return result.scalar_one()
