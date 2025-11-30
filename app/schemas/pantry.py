"""Pydantic schemas for PantryItem model."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ingredient import IngredientRead


class PantryItemBase(BaseModel):
    """Base schema for PantryItem with common fields."""

    ingredient_id: int
    quantity: str | None = Field(default=None, max_length=50)
    unit: str | None = Field(default=None, max_length=30)
    expiration_date: date | None = None


class PantryItemCreate(PantryItemBase):
    """Schema for adding an item to the pantry."""

    pass


class PantryItemBulkCreate(BaseModel):
    """Schema for adding multiple items to the pantry at once."""

    items: list[PantryItemCreate] = Field(
        ..., min_length=1, description="List of pantry items to add"
    )


class PantryItemUpdate(BaseModel):
    """Schema for updating a pantry item."""

    quantity: str | None = Field(default=None, max_length=50)
    unit: str | None = Field(default=None, max_length=30)
    expiration_date: date | None = None


class PantryItemRead(BaseModel):
    """Schema for reading pantry item data (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    quantity: str | None
    unit: str | None
    expiration_date: date | None
    created_at: datetime
    updated_at: datetime
    ingredient: IngredientRead
