"""Pydantic schemas for Favorite model."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.recipe import RecipeSummary


class FavoriteRead(BaseModel):
    """Schema for reading favorite data (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    recipe_id: int
    created_at: datetime
    recipe: RecipeSummary
