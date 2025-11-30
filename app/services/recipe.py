"""Recipe service for database operations."""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.recipe import Recipe, RecipeIngredient
from app.schemas.recipe import RecipeCreate


async def get_recipe_by_id(db: AsyncSession, recipe_id: int) -> Recipe | None:
    """Get a recipe by its ID with all ingredients.

    Args:
        db: Database session.
        recipe_id: Recipe ID to look up.

    Returns:
        Recipe object with ingredients if found, None otherwise.
    """
    result = await db.execute(
        select(Recipe)
        .options(
            selectinload(Recipe.recipe_ingredients).selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(Recipe.id == recipe_id)
    )
    return result.scalar_one_or_none()


async def get_recipes(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    difficulty: str | None = None,
    max_prep_time: int | None = None,
    max_cook_time: int | None = None,
) -> list[Recipe]:
    """Get a paginated list of recipes with optional filters.

    Args:
        db: Database session.
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        difficulty: Filter by difficulty level.
        max_prep_time: Filter by maximum prep time (minutes).
        max_cook_time: Filter by maximum cook time (minutes).

    Returns:
        List of Recipe objects.
    """
    query = select(Recipe).order_by(Recipe.created_at.desc())

    if difficulty:
        query = query.where(Recipe.difficulty_level == difficulty)
    if max_prep_time is not None:
        query = query.where(
            or_(Recipe.prep_time.is_(None), Recipe.prep_time <= max_prep_time)
        )
    if max_cook_time is not None:
        query = query.where(
            or_(Recipe.cook_time.is_(None), Recipe.cook_time <= max_cook_time)
        )

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def search_recipes(
    db: AsyncSession,
    query_text: str,
    skip: int = 0,
    limit: int = 20,
) -> list[Recipe]:
    """Search recipes by title or description.

    Args:
        db: Database session.
        query_text: Search query string.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of matching Recipe objects.
    """
    search_pattern = f"%{query_text}%"

    result = await db.execute(
        select(Recipe)
        .where(
            or_(
                Recipe.title.ilike(search_pattern),
                Recipe.description.ilike(search_pattern),
            )
        )
        .order_by(Recipe.title)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_recipe(db: AsyncSession, recipe_data: RecipeCreate) -> Recipe:
    """Create a new recipe with ingredients.

    Args:
        db: Database session.
        recipe_data: Recipe creation data including ingredients.

    Returns:
        Created Recipe object.
    """
    recipe = Recipe(
        title=recipe_data.title,
        description=recipe_data.description,
        instructions=recipe_data.instructions,
        prep_time=recipe_data.prep_time,
        cook_time=recipe_data.cook_time,
        difficulty_level=recipe_data.difficulty_level,
        servings=recipe_data.servings,
        image_url=recipe_data.image_url,
        source_url=recipe_data.source_url,
    )

    db.add(recipe)
    await db.flush()

    # Add recipe ingredients
    for ing_data in recipe_data.ingredients:
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ing_data.ingredient_id,
            quantity=ing_data.quantity,
            unit=ing_data.unit,
            optional=ing_data.optional,
        )
        db.add(recipe_ingredient)

    await db.flush()
    await db.refresh(recipe)

    # Load relationships
    result = await db.execute(
        select(Recipe)
        .options(
            selectinload(Recipe.recipe_ingredients).selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(Recipe.id == recipe.id)
    )
    return result.scalar_one()


async def count_recipes(
    db: AsyncSession,
    difficulty: str | None = None,
    max_prep_time: int | None = None,
    max_cook_time: int | None = None,
) -> int:
    """Count total recipes with optional filters.

    Args:
        db: Database session.
        difficulty: Filter by difficulty level.
        max_prep_time: Filter by maximum prep time.
        max_cook_time: Filter by maximum cook time.

    Returns:
        Total count of recipes.
    """
    query = select(func.count(Recipe.id))

    if difficulty:
        query = query.where(Recipe.difficulty_level == difficulty)
    if max_prep_time is not None:
        query = query.where(
            or_(Recipe.prep_time.is_(None), Recipe.prep_time <= max_prep_time)
        )
    if max_cook_time is not None:
        query = query.where(
            or_(Recipe.cook_time.is_(None), Recipe.cook_time <= max_cook_time)
        )

    result = await db.execute(query)
    return result.scalar_one()


async def get_all_recipes_with_ingredients(db: AsyncSession) -> list[Recipe]:
    """Get all recipes with their ingredients loaded.

    Used for recommendation matching algorithm.

    Args:
        db: Database session.

    Returns:
        List of all Recipe objects with ingredients.
    """
    result = await db.execute(
        select(Recipe).options(
            selectinload(Recipe.recipe_ingredients).selectinload(
                RecipeIngredient.ingredient
            )
        )
    )
    return list(result.scalars().all())
