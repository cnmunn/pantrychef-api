"""Pydantic schemas for Recipe and RecipeIngredient models."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ingredient import IngredientRead


class RecipeIngredientBase(BaseModel):
    """Base schema for RecipeIngredient."""

    ingredient_id: int
    quantity: str | None = Field(default=None, max_length=50)
    unit: str | None = Field(default=None, max_length=30)
    optional: bool = False


class RecipeIngredientCreate(RecipeIngredientBase):
    """Schema for creating a recipe ingredient association."""

    pass


class RecipeIngredientRead(BaseModel):
    """Schema for reading recipe ingredient data with ingredient details."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity: str | None
    unit: str | None
    optional: bool
    ingredient: IngredientRead


class RecipeBase(BaseModel):
    """Base schema for Recipe with common fields."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    instructions: str = Field(..., min_length=1)
    prep_time: int | None = Field(default=None, ge=0, description="Prep time in minutes")
    cook_time: int | None = Field(default=None, ge=0, description="Cook time in minutes")
    difficulty_level: str | None = Field(
        default=None,
        pattern="^(easy|medium|hard)$",
        description="Difficulty level: easy, medium, or hard",
    )
    servings: int | None = Field(default=None, ge=1)
    image_url: str | None = Field(default=None, max_length=500)
    source_url: str | None = Field(default=None, max_length=500)


class RecipeCreate(RecipeBase):
    """Schema for creating a new recipe."""

    ingredients: list[RecipeIngredientCreate] = Field(
        ..., min_length=1, description="List of ingredients required for the recipe"
    )


class RecipeRead(RecipeBase):
    """Schema for reading recipe data with full details (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    recipe_ingredients: list[RecipeIngredientRead] = Field(
        default_factory=list, description="List of ingredients with quantities"
    )


class RecipeSummary(BaseModel):
    """Schema for recipe summary (list views, search results)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    prep_time: int | None
    cook_time: int | None
    difficulty_level: str | None
    servings: int | None
    image_url: str | None
