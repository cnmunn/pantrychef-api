"""Cooking history service for tracking what users have cooked."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cooking_history import CookingHistory
from app.models.recipe import Recipe
from app.schemas.cooking_history import CookingHistoryCreate, CookingStats
from app.schemas.recipe import RecipeSummary


async def get_history_entry_by_id(
    db: AsyncSession, entry_id: int, user_id: int
) -> CookingHistory | None:
    """Get a cooking history entry by ID for a specific user.

    Args:
        db: Database session.
        entry_id: History entry ID.
        user_id: User ID (for ownership verification).

    Returns:
        CookingHistory if found and owned by user, None otherwise.
    """
    result = await db.execute(
        select(CookingHistory)
        .options(selectinload(CookingHistory.recipe))
        .where(CookingHistory.id == entry_id, CookingHistory.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_cooking_history(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> list[CookingHistory]:
    """Get cooking history for a user.

    Args:
        db: Database session.
        user_id: User ID.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of CookingHistory objects with recipe data.
    """
    result = await db.execute(
        select(CookingHistory)
        .options(selectinload(CookingHistory.recipe))
        .where(CookingHistory.user_id == user_id)
        .order_by(CookingHistory.cooked_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def log_cooked_recipe(
    db: AsyncSession, user_id: int, entry_data: CookingHistoryCreate
) -> CookingHistory:
    """Log a recipe as cooked.

    Args:
        db: Database session.
        user_id: User ID.
        entry_data: Cooking history entry data.

    Returns:
        Created CookingHistory object.
    """
    entry = CookingHistory(
        user_id=user_id,
        recipe_id=entry_data.recipe_id,
        rating=entry_data.rating,
        notes=entry_data.notes,
    )

    db.add(entry)
    await db.flush()
    await db.refresh(entry, ["recipe"])

    return entry


async def get_cooking_stats(db: AsyncSession, user_id: int) -> CookingStats:
    """Get cooking statistics for a user.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        CookingStats with aggregated data.
    """
    # Total recipes cooked (all entries)
    total_result = await db.execute(
        select(func.count(CookingHistory.id)).where(CookingHistory.user_id == user_id)
    )
    total_cooked = total_result.scalar_one()

    # Unique recipes cooked
    unique_result = await db.execute(
        select(func.count(func.distinct(CookingHistory.recipe_id))).where(
            CookingHistory.user_id == user_id
        )
    )
    unique_cooked = unique_result.scalar_one()

    # Average rating (excluding nulls)
    avg_result = await db.execute(
        select(func.avg(CookingHistory.rating)).where(
            CookingHistory.user_id == user_id, CookingHistory.rating.isnot(None)
        )
    )
    avg_rating = avg_result.scalar_one()
    if avg_rating is not None:
        avg_rating = round(float(avg_rating), 2)

    # Most cooked recipe
    most_cooked_result = await db.execute(
        select(CookingHistory.recipe_id, func.count(CookingHistory.id).label("count"))
        .where(CookingHistory.user_id == user_id)
        .group_by(CookingHistory.recipe_id)
        .order_by(func.count(CookingHistory.id).desc())
        .limit(1)
    )
    most_cooked_row = most_cooked_result.first()

    most_cooked_recipe = None
    most_cooked_count = None

    if most_cooked_row:
        recipe_id, count = most_cooked_row
        most_cooked_count = count

        # Get recipe details
        recipe_result = await db.execute(
            select(Recipe).where(Recipe.id == recipe_id)
        )
        recipe = recipe_result.scalar_one_or_none()
        if recipe:
            most_cooked_recipe = RecipeSummary.model_validate(recipe)

    return CookingStats(
        total_recipes_cooked=total_cooked,
        unique_recipes_cooked=unique_cooked,
        average_rating=avg_rating,
        most_cooked_recipe=most_cooked_recipe,
        most_cooked_count=most_cooked_count,
    )
