"""Pydantic schemas for Ingredient model."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    is_vegetarian: bool = Field(
        default=True,
        description="Whether ingredient is suitable for vegetarians (False for meat/fish)",
    )
    is_vegan: bool = Field(
        default=True,
        description="Whether ingredient is suitable for vegans (False for all animal products)",
    )
    is_gluten_free: bool = Field(
        default=True,
        description="Whether ingredient is gluten-free (False for wheat/barley/rye)",
    )
    allergens: str | None = Field(
        default=None,
        max_length=200,
        description="Comma-separated allergen tags (e.g., 'dairy,soy', 'nuts,peanuts')",
    )

    @field_validator("allergens")
    @classmethod
    def normalize_allergens(cls, v: str | None) -> str | None:
        """Normalize allergen string to lowercase, trimmed."""
        if v is None:
            return None
        # Split, clean, lowercase, and rejoin
        allergens = [a.strip().lower() for a in v.split(",") if a.strip()]
        return ",".join(allergens) if allergens else None


class IngredientRead(IngredientBase):
    """Schema for reading ingredient data (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_vegetarian: bool
    is_vegan: bool
    is_gluten_free: bool
    allergens: str | None


class IngredientFilter(BaseModel):
    """Schema for ingredient dietary filters."""

    vegetarian: bool = Field(
        default=False,
        description="Only include vegetarian-friendly recipes",
    )
    vegan: bool = Field(
        default=False,
        description="Only include vegan-friendly recipes",
    )
    gluten_free: bool = Field(
        default=False,
        description="Only include gluten-free recipes",
    )
    exclude_allergens: list[str] = Field(
        default_factory=list,
        description="List of allergens to exclude (e.g., ['dairy', 'nuts'])",
    )
