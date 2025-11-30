"""Service layer for business logic."""

from app.services.cooking_history import (
    get_cooking_stats,
    get_history_entry_by_id,
    get_user_cooking_history,
    log_cooked_recipe,
)
from app.services.favorite import (
    add_favorite,
    get_favorite_by_id,
    get_favorite_by_recipe,
    get_user_favorites,
    remove_favorite,
)
from app.services.ingredient import (
    count_ingredients,
    create_ingredient,
    get_all_categories,
    get_ingredient_by_id,
    get_ingredient_by_name,
    get_ingredients,
)
from app.services.pantry import (
    create_pantry_item,
    create_pantry_items_bulk,
    delete_pantry_item,
    get_expiring_items,
    get_pantry_item_by_id,
    get_pantry_item_by_ingredient,
    get_user_pantry_ingredient_ids,
    get_user_pantry_items,
    update_pantry_item,
)
from app.services.recipe import (
    count_recipes,
    create_recipe,
    get_all_recipes_with_ingredients,
    get_recipe_by_id,
    get_recipes,
    search_recipes,
)
from app.services.recommendation import (
    get_recipe_recommendations,
    get_shopping_list,
)
from app.services.user import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
)

__all__ = [
    # User services
    "create_user",
    "get_user_by_email",
    "get_user_by_id",
    "get_user_by_username",
    # Ingredient services
    "count_ingredients",
    "create_ingredient",
    "get_all_categories",
    "get_ingredient_by_id",
    "get_ingredient_by_name",
    "get_ingredients",
    # Pantry services
    "create_pantry_item",
    "create_pantry_items_bulk",
    "delete_pantry_item",
    "get_expiring_items",
    "get_pantry_item_by_id",
    "get_pantry_item_by_ingredient",
    "get_user_pantry_ingredient_ids",
    "get_user_pantry_items",
    "update_pantry_item",
    # Recipe services
    "count_recipes",
    "create_recipe",
    "get_all_recipes_with_ingredients",
    "get_recipe_by_id",
    "get_recipes",
    "search_recipes",
    # Recommendation services
    "get_recipe_recommendations",
    "get_shopping_list",
    # Favorite services
    "add_favorite",
    "get_favorite_by_id",
    "get_favorite_by_recipe",
    "get_user_favorites",
    "remove_favorite",
    # Cooking history services
    "get_cooking_stats",
    "get_history_entry_by_id",
    "get_user_cooking_history",
    "log_cooked_recipe",
]
