"""Pydantic schemas for Ingredient model."""

from pydantic import BaseModel, ConfigDict, Field


class IngredientBase(BaseModel):
    """Base schema for Ingredient with common fields."""

    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Category of ingredient (e.g., produce, dairy, protein, grains, spices)",
    )


class IngredientCreate(IngredientBase):
    """Schema for creating a new ingredient."""

    pass


class IngredientRead(IngredientBase):
    """Schema for reading ingredient data (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
