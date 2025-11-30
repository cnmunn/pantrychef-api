"""Pantry router for managing user's ingredient inventory."""

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import (
    Message,
    PantryItemBulkCreate,
    PantryItemCreate,
    PantryItemRead,
    PantryItemUpdate,
)
from app.services.ingredient import get_ingredient_by_id
from app.services.pantry import (
    create_pantry_item,
    create_pantry_items_bulk,
    delete_pantry_item,
    get_expiring_items,
    get_pantry_item_by_id,
    get_pantry_item_by_ingredient,
    get_user_pantry_items,
    update_pantry_item,
)
from app.utils.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/pantry", tags=["Pantry"])


@router.get(
    "/",
    response_model=list[PantryItemRead],
    summary="List user's pantry items",
    responses={
        200: {"description": "List of pantry items"},
        401: {"description": "Not authenticated"},
    },
)
async def list_pantry_items(
    db: DbSession,
    current_user: CurrentUser,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
) -> list[PantryItemRead]:
    """Get all items in the current user's pantry.

    Returns a list of pantry items with ingredient details, ordered by most recently added.
    Use `skip` and `limit` for pagination.
    """
    items = await get_user_pantry_items(db, current_user.id, skip=skip, limit=limit)
    return [PantryItemRead.model_validate(item) for item in items]


@router.get(
    "/expiring",
    response_model=list[PantryItemRead],
    summary="Get expiring pantry items",
    responses={
        200: {"description": "List of expiring items"},
        401: {"description": "Not authenticated"},
    },
)
async def list_expiring_items(
    db: DbSession,
    current_user: CurrentUser,
    days: int = Query(7, ge=1, le=90, description="Days to look ahead for expiration"),
) -> list[PantryItemRead]:
    """Get pantry items expiring within the specified number of days.

    Useful for planning meals around ingredients that need to be used soon.
    Items are sorted by expiration date (soonest first).
    """
    items = await get_expiring_items(db, current_user.id, days=days)
    return [PantryItemRead.model_validate(item) for item in items]


@router.get(
    "/{item_id}",
    response_model=PantryItemRead,
    summary="Get pantry item by ID",
    responses={
        200: {"description": "Pantry item details"},
        401: {"description": "Not authenticated"},
        404: {"description": "Pantry item not found"},
    },
)
async def get_pantry_item(
    item_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> PantryItemRead:
    """Get a specific pantry item by its ID."""
    item = await get_pantry_item_by_id(db, item_id, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pantry item with ID {item_id} not found",
        )
    return PantryItemRead.model_validate(item)


@router.post(
    "/",
    response_model=PantryItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to pantry",
    responses={
        201: {"description": "Item added to pantry"},
        400: {"description": "Invalid ingredient or already in pantry"},
        401: {"description": "Not authenticated"},
    },
)
async def add_pantry_item(
    item_data: PantryItemCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> PantryItemRead:
    """Add a new item to your pantry.

    - **ingredient_id**: ID of the ingredient to add
    - **quantity**: Optional quantity (e.g., "2", "500g")
    - **unit**: Optional unit of measurement (e.g., "cups", "pieces")
    - **expiration_date**: Optional expiration date

    Note: Each ingredient can only be added once per user. To update quantity,
    use the PATCH endpoint.
    """
    # Verify ingredient exists
    ingredient = await get_ingredient_by_id(db, item_data.ingredient_id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with ID {item_data.ingredient_id} not found",
        )

    # Check if already in pantry
    existing = await get_pantry_item_by_ingredient(
        db, current_user.id, item_data.ingredient_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{ingredient.name}' is already in your pantry. Use PATCH to update.",
        )

    item = await create_pantry_item(db, current_user.id, item_data)
    return PantryItemRead.model_validate(item)


@router.post(
    "/bulk",
    response_model=list[PantryItemRead],
    status_code=status.HTTP_201_CREATED,
    summary="Add multiple items to pantry",
    responses={
        201: {"description": "Items added to pantry"},
        400: {"description": "Invalid ingredient(s)"},
        401: {"description": "Not authenticated"},
    },
)
async def add_pantry_items_bulk(
    bulk_data: PantryItemBulkCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> list[PantryItemRead]:
    """Add multiple items to your pantry at once.

    Useful for initial pantry setup or after grocery shopping.
    Items that already exist in the pantry will be skipped.
    """
    # Verify all ingredients exist and filter out existing items
    valid_items = []
    for item_data in bulk_data.items:
        ingredient = await get_ingredient_by_id(db, item_data.ingredient_id)
        if not ingredient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ingredient with ID {item_data.ingredient_id} not found",
            )

        # Skip if already in pantry
        existing = await get_pantry_item_by_ingredient(
            db, current_user.id, item_data.ingredient_id
        )
        if not existing:
            valid_items.append(item_data)

    if not valid_items:
        return []

    items = await create_pantry_items_bulk(db, current_user.id, valid_items)
    return [PantryItemRead.model_validate(item) for item in items]


@router.patch(
    "/{item_id}",
    response_model=PantryItemRead,
    summary="Update pantry item",
    responses={
        200: {"description": "Item updated"},
        401: {"description": "Not authenticated"},
        404: {"description": "Pantry item not found"},
    },
)
async def update_pantry_item_endpoint(
    item_id: int,
    update_data: PantryItemUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> PantryItemRead:
    """Update a pantry item's quantity, unit, or expiration date.

    Only provided fields will be updated. Use `null` to clear a field.
    """
    item = await get_pantry_item_by_id(db, item_id, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pantry item with ID {item_id} not found",
        )

    updated_item = await update_pantry_item(db, item, update_data)
    return PantryItemRead.model_validate(updated_item)


@router.delete(
    "/{item_id}",
    response_model=Message,
    summary="Remove item from pantry",
    responses={
        200: {"description": "Item removed"},
        401: {"description": "Not authenticated"},
        404: {"description": "Pantry item not found"},
    },
)
async def remove_pantry_item(
    item_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Message:
    """Remove an item from your pantry."""
    deleted = await delete_pantry_item(db, item_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pantry item with ID {item_id} not found",
        )
    return Message(message="Item removed from pantry")
