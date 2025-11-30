"""Pydantic schemas for request/response validation."""

from app.schemas.common import (
    Message,
    PaginatedResponse,
    RecipeMatch,
    ShoppingList,
    ShoppingListItem,
    Token,
    TokenData,
)
from app.schemas.cooking_history import (
    CookingHistoryCreate,
    CookingHistoryRead,
    CookingStats,
)
from app.schemas.favorite import FavoriteRead
from app.schemas.ingredient import IngredientCreate, IngredientRead
from app.schemas.pantry import (
    PantryItemBulkCreate,
    PantryItemCreate,
    PantryItemRead,
    PantryItemUpdate,
)
from app.schemas.recipe import (
    RecipeCreate,
    RecipeIngredientCreate,
    RecipeIngredientRead,
    RecipeRead,
    RecipeSummary,
)
from app.schemas.user import UserCreate, UserRead, UserUpdate

__all__ = [
    # User schemas
    "UserCreate",
    "UserRead",
    "UserUpdate",
    # Ingredient schemas
    "IngredientCreate",
    "IngredientRead",
    # Recipe schemas
    "RecipeCreate",
    "RecipeRead",
    "RecipeSummary",
    "RecipeIngredientCreate",
    "RecipeIngredientRead",
    # Pantry schemas
    "PantryItemCreate",
    "PantryItemRead",
    "PantryItemUpdate",
    "PantryItemBulkCreate",
    # Favorite schemas
    "FavoriteRead",
    # Cooking history schemas
    "CookingHistoryCreate",
    "CookingHistoryRead",
    "CookingStats",
    # Common schemas
    "PaginatedResponse",
    "RecipeMatch",
    "ShoppingList",
    "ShoppingListItem",
    "Token",
    "TokenData",
    "Message",
]
