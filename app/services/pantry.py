"""Pantry service for managing user's ingredient inventory."""

from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pantry import PantryItem
from app.schemas.pantry import PantryItemCreate, PantryItemUpdate


async def get_pantry_item_by_id(
    db: AsyncSession, item_id: int, user_id: int
) -> PantryItem | None:
    """Get a pantry item by ID for a specific user.

    Args:
        db: Database session.
        item_id: Pantry item ID.
        user_id: User ID (for ownership verification).

    Returns:
        PantryItem if found and owned by user, None otherwise.
    """
    result = await db.execute(
        select(PantryItem)
        .options(selectinload(PantryItem.ingredient))
        .where(PantryItem.id == item_id, PantryItem.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_pantry_items(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> list[PantryItem]:
    """Get all pantry items for a user.

    Args:
        db: Database session.
        user_id: User ID.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        List of PantryItem objects with ingredient data.
    """
    result = await db.execute(
        select(PantryItem)
        .options(selectinload(PantryItem.ingredient))
        .where(PantryItem.user_id == user_id)
        .order_by(PantryItem.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_user_pantry_ingredient_ids(db: AsyncSession, user_id: int) -> set[int]:
    """Get set of ingredient IDs in user's pantry.

    Args:
        db: Database session.
        user_id: User ID.

    Returns:
        Set of ingredient IDs.
    """
    result = await db.execute(
        select(PantryItem.ingredient_id).where(PantryItem.user_id == user_id)
    )
    return set(result.scalars().all())


async def get_pantry_item_by_ingredient(
    db: AsyncSession, user_id: int, ingredient_id: int
) -> PantryItem | None:
    """Check if user already has an ingredient in their pantry.

    Args:
        db: Database session.
        user_id: User ID.
        ingredient_id: Ingredient ID to check.

    Returns:
        PantryItem if exists, None otherwise.
    """
    result = await db.execute(
        select(PantryItem)
        .options(selectinload(PantryItem.ingredient))
        .where(PantryItem.user_id == user_id, PantryItem.ingredient_id == ingredient_id)
    )
    return result.scalar_one_or_none()


async def create_pantry_item(
    db: AsyncSession, user_id: int, item_data: PantryItemCreate
) -> PantryItem:
    """Add an item to user's pantry.

    Args:
        db: Database session.
        user_id: User ID.
        item_data: Pantry item creation data.

    Returns:
        Created PantryItem object.
    """
    item = PantryItem(
        user_id=user_id,
        ingredient_id=item_data.ingredient_id,
        quantity=item_data.quantity,
        unit=item_data.unit,
        expiration_date=item_data.expiration_date,
    )

    db.add(item)
    await db.flush()
    await db.refresh(item, ["ingredient"])

    return item


async def create_pantry_items_bulk(
    db: AsyncSession, user_id: int, items_data: list[PantryItemCreate]
) -> list[PantryItem]:
    """Add multiple items to user's pantry.

    Args:
        db: Database session.
        user_id: User ID.
        items_data: List of pantry item creation data.

    Returns:
        List of created PantryItem objects.
    """
    items = [
        PantryItem(
            user_id=user_id,
            ingredient_id=item_data.ingredient_id,
            quantity=item_data.quantity,
            unit=item_data.unit,
            expiration_date=item_data.expiration_date,
        )
        for item_data in items_data
    ]

    db.add_all(items)
    await db.flush()

    # Refresh all items to get relationships
    for item in items:
        await db.refresh(item, ["ingredient"])

    return items


async def update_pantry_item(
    db: AsyncSession, item: PantryItem, update_data: PantryItemUpdate
) -> PantryItem:
    """Update a pantry item.

    Args:
        db: Database session.
        item: PantryItem to update.
        update_data: Update data.

    Returns:
        Updated PantryItem object.
    """
    update_dict = update_data.model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        setattr(item, field, value)

    await db.flush()
    # Refresh all attributes including updated_at, then load the ingredient relationship
    await db.refresh(item)
    await db.refresh(item, ["ingredient"])

    return item


async def delete_pantry_item(db: AsyncSession, item_id: int, user_id: int) -> bool:
    """Delete a pantry item.

    Args:
        db: Database session.
        item_id: Pantry item ID.
        user_id: User ID (for ownership verification).

    Returns:
        True if deleted, False if not found.
    """
    result = await db.execute(
        delete(PantryItem).where(
            PantryItem.id == item_id, PantryItem.user_id == user_id
        )
    )
    return result.rowcount > 0


async def get_expiring_items(
    db: AsyncSession, user_id: int, days: int = 7
) -> list[PantryItem]:
    """Get pantry items expiring within specified days.

    Args:
        db: Database session.
        user_id: User ID.
        days: Number of days to look ahead.

    Returns:
        List of expiring PantryItem objects.
    """
    from datetime import timedelta

    today = date.today()
    expiry_threshold = today + timedelta(days=days)

    result = await db.execute(
        select(PantryItem)
        .options(selectinload(PantryItem.ingredient))
        .where(
            PantryItem.user_id == user_id,
            PantryItem.expiration_date.isnot(None),
            PantryItem.expiration_date <= expiry_threshold,
        )
        .order_by(PantryItem.expiration_date)
    )
    return list(result.scalars().all())
