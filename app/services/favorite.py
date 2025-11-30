"""Favorite service for managing user's favorite recipes."""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.favorite import Favorite


async def get_favorite_by_id(
    db: AsyncSession, favorite_id: int, user_id: int
) -> Favorite | None:
    """Get a favorite by ID for a specific user.

    Args:
        db: Database session.
        favorite_id: Favorite ID.
        user_id: User ID (for ownership verification).

    Returns:
        Favorite if found and owned by user, None otherwise.
    """
    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.recipe))
        .where(Favorite.id == favorite_id, Favorite.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_favorite_by_recipe(
    db: AsyncSession, user_id: int, recipe_id: int
) -> Favorite | None:
    """Check if a recipe is in user's favorites.

    Args:
        db: Database session.
        user_id: User ID.
        recipe_id: Recipe ID.

    Returns:
        Favorite if exists, None otherwise.
    """
    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.recipe))
        .where(Favorite.user_id == user_id, Favorite.recipe_id == recipe_id)
    )
    return result.scalar_one_or_none()


async def get_user_favorites(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
) -> list[Favorite]:
    """Get all favorites for a user.

    Args:
        db: Database session.
        user_id: User ID.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of Favorite objects with recipe data.
    """
    result = await db.execute(
        select(Favorite)
        .options(selectinload(Favorite.recipe))
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def add_favorite(db: AsyncSession, user_id: int, recipe_id: int) -> Favorite:
    """Add a recipe to user's favorites.

    Args:
        db: Database session.
        user_id: User ID.
        recipe_id: Recipe ID.

    Returns:
        Created Favorite object.
    """
    favorite = Favorite(user_id=user_id, recipe_id=recipe_id)

    db.add(favorite)
    await db.flush()
    await db.refresh(favorite, ["recipe"])

    return favorite


async def remove_favorite(db: AsyncSession, user_id: int, recipe_id: int) -> bool:
    """Remove a recipe from user's favorites.

    Args:
        db: Database session.
        user_id: User ID.
        recipe_id: Recipe ID.

    Returns:
        True if removed, False if not found.
    """
    result = await db.execute(
        delete(Favorite).where(
            Favorite.user_id == user_id, Favorite.recipe_id == recipe_id
        )
    )
    return result.rowcount > 0
