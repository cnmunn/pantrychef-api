"""Common/shared Pydantic schemas."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ingredient import IngredientRead
from app.schemas.recipe import RecipeSummary


class PaginatedResponse[T](BaseModel):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")

    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1


class RecipeMatch(RecipeSummary):
    """Recipe with match percentage based on pantry ingredients."""

    model_config = ConfigDict(from_attributes=True)

    match_percentage: float = Field(
        ..., ge=0, le=100, description="Percentage of required ingredients user has"
    )
    matched_ingredients: int = Field(..., ge=0, description="Number of matched ingredients")
    total_required_ingredients: int = Field(
        ..., ge=0, description="Total required (non-optional) ingredients"
    )
    missing_ingredients: list[IngredientRead] = Field(
        default_factory=list, description="List of ingredients user is missing"
    )
    uses_expiring_ingredients: int | None = Field(
        default=None,
        ge=0,
        description="Number of soon-to-expire ingredients used (when prioritize_expiring=true)",
    )


class ShoppingListItem(BaseModel):
    """An item needed for a recipe that's not in the user's pantry."""

    ingredient: IngredientRead
    quantity: str | None
    unit: str | None


class ShoppingList(BaseModel):
    """Shopping list for a recipe based on user's pantry."""

    recipe_id: int
    recipe_title: str
    missing_items: list[ShoppingListItem]
    total_missing: int


class Token(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data extracted from JWT token."""

    user_id: int | None = None
    email: str | None = None


class Message(BaseModel):
    """Simple message response."""

    message: str
