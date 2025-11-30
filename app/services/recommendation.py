"""Recommendation service for recipe matching based on pantry ingredients."""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pantry import PantryItem
from app.models.recipe import Recipe, RecipeIngredient
from app.schemas.common import RecipeMatch, ShoppingList, ShoppingListItem
from app.schemas.ingredient import IngredientRead
from app.services.pantry import get_user_pantry_ingredient_ids


def _check_dietary_compatibility(
    recipe_ingredients: list[RecipeIngredient],
    vegetarian: bool = False,
    vegan: bool = False,
    gluten_free: bool = False,
    exclude_allergens: list[str] | None = None,
) -> bool:
    """Check if a recipe meets dietary requirements.

    A recipe is compatible if ALL its required ingredients meet the criteria.

    Args:
        recipe_ingredients: List of recipe ingredients.
        vegetarian: If True, all ingredients must be vegetarian.
        vegan: If True, all ingredients must be vegan.
        gluten_free: If True, all ingredients must be gluten-free.
        exclude_allergens: List of allergens to exclude.

    Returns:
        True if recipe is compatible, False otherwise.
    """
    exclude_allergens = exclude_allergens or []
    exclude_allergens_lower = [a.lower() for a in exclude_allergens]

    for ri in recipe_ingredients:
        if ri.optional:
            continue  # Optional ingredients don't disqualify a recipe

        ingredient = ri.ingredient

        # Check vegetarian
        if vegetarian and not ingredient.is_vegetarian:
            return False

        # Check vegan
        if vegan and not ingredient.is_vegan:
            return False

        # Check gluten-free
        if gluten_free and not ingredient.is_gluten_free:
            return False

        # Check allergens
        if exclude_allergens_lower:
            ingredient_allergens = ingredient.get_allergen_list()
            for allergen in ingredient_allergens:
                if allergen in exclude_allergens_lower:
                    return False

    return True


async def get_expiring_ingredient_ids(
    db: AsyncSession, user_id: int, days: int = 7
) -> set[int]:
    """Get ingredient IDs that are expiring soon in user's pantry.

    Args:
        db: Database session.
        user_id: User ID.
        days: Number of days to consider as "expiring soon".

    Returns:
        Set of ingredient IDs expiring within the specified days.
    """
    today = date.today()
    expiry_threshold = today + timedelta(days=days)

    result = await db.execute(
        select(PantryItem.ingredient_id).where(
            PantryItem.user_id == user_id,
            PantryItem.expiration_date.isnot(None),
            PantryItem.expiration_date <= expiry_threshold,
            PantryItem.expiration_date >= today,  # Not already expired
        )
    )
    return set(result.scalars().all())


async def get_recipe_recommendations(
    db: AsyncSession,
    user_id: int,
    min_match_percent: float = 0.0,
    max_missing_ingredients: int | None = None,
    difficulty: str | None = None,
    max_total_time: int | None = None,
    vegetarian: bool = False,
    vegan: bool = False,
    gluten_free: bool = False,
    exclude_allergens: list[str] | None = None,
    prioritize_expiring: bool = False,
    limit: int = 20,
) -> list[RecipeMatch]:
    """Get recipe recommendations ranked by pantry ingredient match.

    The core recommendation algorithm:
    1. Get user's pantry ingredients
    2. For each recipe, calculate what percentage of required ingredients the user has
    3. Apply dietary filters
    4. Rank recipes by match percentage (highest first)
    5. Optionally boost recipes using soon-to-expire ingredients

    Args:
        db: Database session.
        user_id: User ID.
        min_match_percent: Minimum match percentage (0-100).
        max_missing_ingredients: Maximum number of missing ingredients allowed.
        difficulty: Filter by difficulty level.
        max_total_time: Filter by max prep + cook time.
        vegetarian: Only include vegetarian recipes.
        vegan: Only include vegan recipes.
        gluten_free: Only include gluten-free recipes.
        exclude_allergens: List of allergens to exclude.
        prioritize_expiring: Boost recipes using soon-to-expire ingredients.
        limit: Maximum number of recipes to return.

    Returns:
        List of RecipeMatch objects sorted by match percentage.
    """
    # Get user's pantry ingredient IDs
    pantry_ingredient_ids = await get_user_pantry_ingredient_ids(db, user_id)

    # Get expiring ingredient IDs if prioritizing
    expiring_ids: set[int] = set()
    if prioritize_expiring:
        expiring_ids = await get_expiring_ingredient_ids(db, user_id)

    # Get all recipes with ingredients
    result = await db.execute(
        select(Recipe).options(
            selectinload(Recipe.recipe_ingredients).selectinload(
                RecipeIngredient.ingredient
            )
        )
    )
    recipes = list(result.scalars().all())

    matches: list[RecipeMatch] = []

    for recipe in recipes:
        # Apply difficulty filter
        if difficulty and recipe.difficulty_level != difficulty:
            continue

        # Apply time filter
        if max_total_time is not None:
            total_time = (recipe.prep_time or 0) + (recipe.cook_time or 0)
            if total_time > max_total_time:
                continue

        # Apply dietary filters
        if not _check_dietary_compatibility(
            recipe.recipe_ingredients,
            vegetarian=vegetarian,
            vegan=vegan,
            gluten_free=gluten_free,
            exclude_allergens=exclude_allergens,
        ):
            continue

        # Calculate match for required (non-optional) ingredients only
        required_ingredients = [
            ri for ri in recipe.recipe_ingredients if not ri.optional
        ]

        if not required_ingredients:
            # Recipe has no required ingredients, 100% match
            match_percentage = 100.0
            matched_count = 0
            missing = []
            uses_expiring = 0
        else:
            matched_count = sum(
                1
                for ri in required_ingredients
                if ri.ingredient_id in pantry_ingredient_ids
            )
            total_required = len(required_ingredients)
            match_percentage = (matched_count / total_required) * 100

            # Count how many expiring ingredients this recipe uses
            uses_expiring = sum(
                1
                for ri in required_ingredients
                if ri.ingredient_id in expiring_ids
            )

            # Get missing ingredients
            missing = [
                IngredientRead.model_validate(ri.ingredient)
                for ri in required_ingredients
                if ri.ingredient_id not in pantry_ingredient_ids
            ]

        # Apply filters
        if match_percentage < min_match_percent:
            continue

        if max_missing_ingredients is not None and len(missing) > max_missing_ingredients:
            continue

        matches.append(
            RecipeMatch(
                id=recipe.id,
                title=recipe.title,
                description=recipe.description,
                prep_time=recipe.prep_time,
                cook_time=recipe.cook_time,
                difficulty_level=recipe.difficulty_level,
                servings=recipe.servings,
                image_url=recipe.image_url,
                match_percentage=round(match_percentage, 1),
                matched_ingredients=matched_count,
                total_required_ingredients=len(required_ingredients),
                missing_ingredients=missing,
                uses_expiring_ingredients=uses_expiring if prioritize_expiring else None,
            )
        )

    # Sort by:
    # 1. If prioritizing expiring: number of expiring ingredients used (descending)
    # 2. Match percentage (descending)
    # 3. Title (alphabetically)
    if prioritize_expiring:
        matches.sort(
            key=lambda m: (
                -(m.uses_expiring_ingredients or 0),
                -m.match_percentage,
                m.title,
            )
        )
    else:
        matches.sort(key=lambda m: (-m.match_percentage, m.title))

    return matches[:limit]


async def get_shopping_list(
    db: AsyncSession, user_id: int, recipe_id: int
) -> ShoppingList | None:
    """Generate a shopping list for a recipe based on user's pantry.

    Args:
        db: Database session.
        user_id: User ID.
        recipe_id: Recipe ID.

    Returns:
        ShoppingList with missing ingredients, or None if recipe not found.
    """
    # Get recipe with ingredients
    result = await db.execute(
        select(Recipe)
        .options(
            selectinload(Recipe.recipe_ingredients).selectinload(
                RecipeIngredient.ingredient
            )
        )
        .where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        return None

    # Get user's pantry ingredient IDs
    pantry_ingredient_ids = await get_user_pantry_ingredient_ids(db, user_id)

    # Find missing ingredients (including optional ones for shopping list)
    missing_items = [
        ShoppingListItem(
            ingredient=IngredientRead.model_validate(ri.ingredient),
            quantity=ri.quantity,
            unit=ri.unit,
        )
        for ri in recipe.recipe_ingredients
        if ri.ingredient_id not in pantry_ingredient_ids
    ]

    return ShoppingList(
        recipe_id=recipe.id,
        recipe_title=recipe.title,
        missing_items=missing_items,
        total_missing=len(missing_items),
    )
