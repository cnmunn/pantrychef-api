"""Pydantic schemas for CookingHistory model."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.recipe import RecipeSummary


class CookingHistoryBase(BaseModel):
    """Base schema for CookingHistory with common fields."""

    recipe_id: int
    rating: int | None = Field(default=None, ge=1, le=5, description="Rating from 1 to 5 stars")
    notes: str | None = None


class CookingHistoryCreate(CookingHistoryBase):
    """Schema for logging a cooked recipe."""

    pass


class CookingHistoryRead(BaseModel):
    """Schema for reading cooking history data (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    recipe_id: int
    cooked_at: datetime
    rating: int | None
    notes: str | None
    recipe: RecipeSummary


class CookingStats(BaseModel):
    """Schema for cooking statistics."""

    total_recipes_cooked: int
    unique_recipes_cooked: int
    average_rating: float | None
    most_cooked_recipe: RecipeSummary | None
    most_cooked_count: int | None
