"""Tests for recommendation endpoints and matching algorithm."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.user import User
from app.services.recommendation import (
    _check_dietary_compatibility,
    get_recipe_recommendations,
    get_shopping_list,
)
from tests.conftest import (
    IngredientFactory,
    PantryItemFactory,
    RecipeFactory,
    get_auth_headers,
)


# =============================================================================
# UNIT TESTS FOR MATCHING ALGORITHM
# =============================================================================

class TestDietaryCompatibility:
    """Unit tests for _check_dietary_compatibility function."""

    async def test_all_vegetarian_recipe(
        self,
        db_session: AsyncSession,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
    ):
        """Test vegetarian recipe passes vegetarian check."""
        tomato = await ingredient_factory.create(
            name="Tomato", is_vegetarian=True, is_vegan=True
        )
        pasta = await ingredient_factory.create(
            name="Pasta", is_vegetarian=True, is_vegan=True
        )
        
        recipe = await recipe_factory.create(
            title="Pasta Pomodoro",
            ingredients=[
                (tomato, "4", "medium", False),
                (pasta, "1", "pound", False),
            ],
        )
        
        # Reload recipe with ingredients
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.recipe import Recipe, RecipeIngredient
        
        result = await db_session.execute(
            select(Recipe)
            .options(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))
            .where(Recipe.id == recipe.id)
        )
        recipe = result.scalar_one()
        
        assert _check_dietary_compatibility(
            recipe.recipe_ingredients, vegetarian=True
        ) is True

    async def test_non_vegetarian_recipe_fails(
        self,
        db_session: AsyncSession,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
    ):
        """Test recipe with meat fails vegetarian check."""
        chicken = await ingredient_factory.create(
            name="Chicken", is_vegetarian=False, is_vegan=False
        )
        
        recipe = await recipe_factory.create(
            title="Chicken Dinner",
            ingredients=[(chicken, "1", "pound", False)],
        )
        
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.recipe import Recipe, RecipeIngredient
        
        result = await db_session.execute(
            select(Recipe)
            .options(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))
            .where(Recipe.id == recipe.id)
        )
        recipe = result.scalar_one()
        
        assert _check_dietary_compatibility(
            recipe.recipe_ingredients, vegetarian=True
        ) is False

    async def test_optional_non_vegan_passes(
        self,
        db_session: AsyncSession,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
    ):
        """Test that optional non-vegan ingredients don't disqualify recipe."""
        tomato = await ingredient_factory.create(
            name="Tomato", is_vegan=True
        )
        cheese = await ingredient_factory.create(
            name="Cheese", is_vegan=False, allergens="dairy"
        )
        
        recipe = await recipe_factory.create(
            title="Salad",
            ingredients=[
                (tomato, "2", "medium", False),
                (cheese, "1/2", "cup", True),  # Optional
            ],
        )
        
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.recipe import Recipe, RecipeIngredient
        
        result = await db_session.execute(
            select(Recipe)
            .options(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))
            .where(Recipe.id == recipe.id)
        )
        recipe = result.scalar_one()
        
        assert _check_dietary_compatibility(
            recipe.recipe_ingredients, vegan=True
        ) is True

    async def test_allergen_exclusion(
        self,
        db_session: AsyncSession,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
    ):
        """Test allergen exclusion works correctly."""
        tomato = await ingredient_factory.create(name="Tomato")
        peanuts = await ingredient_factory.create(
            name="Peanuts", allergens="peanuts,nuts"
        )
        
        recipe = await recipe_factory.create(
            title="Peanut Salad",
            ingredients=[
                (tomato, "2", "medium", False),
                (peanuts, "1/4", "cup", False),
            ],
        )
        
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.recipe import Recipe, RecipeIngredient
        
        result = await db_session.execute(
            select(Recipe)
            .options(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))
            .where(Recipe.id == recipe.id)
        )
        recipe = result.scalar_one()
        
        # Should fail with peanut allergy
        assert _check_dietary_compatibility(
            recipe.recipe_ingredients, exclude_allergens=["peanuts"]
        ) is False
        
        # Should pass without peanut allergy
        assert _check_dietary_compatibility(
            recipe.recipe_ingredients, exclude_allergens=[]
        ) is True


class TestRecipeMatching:
    """Unit tests for recipe matching algorithm."""

    async def test_perfect_match(
        self,
        db_session: AsyncSession,
        test_user: User,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test recipe with 100% ingredient match."""
        tomato = await ingredient_factory.create(name="Tomato")
        onion = await ingredient_factory.create(name="Onion")
        
        recipe = await recipe_factory.create(
            title="Tomato Onion Salad",
            ingredients=[
                (tomato, "2", "medium", False),
                (onion, "1", "medium", False),
            ],
        )
        
        # User has all ingredients
        await pantry_factory.create(test_user, tomato)
        await pantry_factory.create(test_user, onion)
        
        matches = await get_recipe_recommendations(db_session, test_user.id)
        
        assert len(matches) == 1
        assert matches[0].match_percentage == 100.0
        assert matches[0].matched_ingredients == 2
        assert matches[0].total_required_ingredients == 2
        assert len(matches[0].missing_ingredients) == 0

    async def test_partial_match(
        self,
        db_session: AsyncSession,
        test_user: User,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test recipe with partial ingredient match."""
        tomato = await ingredient_factory.create(name="Tomato")
        onion = await ingredient_factory.create(name="Onion")
        garlic = await ingredient_factory.create(name="Garlic")
        
        recipe = await recipe_factory.create(
            title="Three Ingredient Recipe",
            ingredients=[
                (tomato, "2", "medium", False),
                (onion, "1", "medium", False),
                (garlic, "2", "cloves", False),
            ],
        )
        
        # User has only 2 of 3 ingredients
        await pantry_factory.create(test_user, tomato)
        await pantry_factory.create(test_user, onion)
        
        matches = await get_recipe_recommendations(db_session, test_user.id)
        
        assert len(matches) == 1
        assert matches[0].match_percentage == pytest.approx(66.7, abs=0.1)
        assert matches[0].matched_ingredients == 2
        assert matches[0].total_required_ingredients == 3
        assert len(matches[0].missing_ingredients) == 1
        assert matches[0].missing_ingredients[0].name == "Garlic"

    async def test_min_match_percent_filter(
        self,
        db_session: AsyncSession,
        test_user: User,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test filtering by minimum match percentage."""
        tomato = await ingredient_factory.create(name="Tomato")
        onion = await ingredient_factory.create(name="Onion")
        garlic = await ingredient_factory.create(name="Garlic")
        
        # Recipe with 50% match potential
        await recipe_factory.create(
            title="Low Match Recipe",
            ingredients=[
                (tomato, "2", "medium", False),
                (onion, "1", "medium", False),
            ],
        )
        
        # User has only tomato (50% match)
        await pantry_factory.create(test_user, tomato)
        
        # With 60% minimum, should return no results
        matches = await get_recipe_recommendations(
            db_session, test_user.id, min_match_percent=60.0
        )
        assert len(matches) == 0
        
        # With 40% minimum, should return the recipe
        matches = await get_recipe_recommendations(
            db_session, test_user.id, min_match_percent=40.0
        )
        assert len(matches) == 1

    async def test_difficulty_filter(
        self,
        db_session: AsyncSession,
        test_user: User,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test filtering by difficulty level."""
        tomato = await ingredient_factory.create(name="Tomato")
        await pantry_factory.create(test_user, tomato)
        
        await recipe_factory.create(
            title="Easy Recipe",
            difficulty_level="easy",
            ingredients=[(tomato, "1", "medium", False)],
        )
        await recipe_factory.create(
            title="Hard Recipe",
            difficulty_level="hard",
            ingredients=[(tomato, "1", "medium", False)],
        )
        
        matches = await get_recipe_recommendations(
            db_session, test_user.id, difficulty="easy"
        )
        
        assert len(matches) == 1
        assert matches[0].title == "Easy Recipe"

    async def test_max_time_filter(
        self,
        db_session: AsyncSession,
        test_user: User,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test filtering by maximum total time."""
        tomato = await ingredient_factory.create(name="Tomato")
        await pantry_factory.create(test_user, tomato)
        
        await recipe_factory.create(
            title="Quick Recipe",
            prep_time=5,
            cook_time=10,
            ingredients=[(tomato, "1", "medium", False)],
        )
        await recipe_factory.create(
            title="Slow Recipe",
            prep_time=30,
            cook_time=60,
            ingredients=[(tomato, "1", "medium", False)],
        )
        
        matches = await get_recipe_recommendations(
            db_session, test_user.id, max_total_time=30
        )
        
        assert len(matches) == 1
        assert matches[0].title == "Quick Recipe"

    async def test_expiring_ingredient_priority(
        self,
        db_session: AsyncSession,
        test_user: User,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test recipes using expiring ingredients are prioritized."""
        tomato = await ingredient_factory.create(name="Tomato")
        onion = await ingredient_factory.create(name="Onion")
        
        await recipe_factory.create(
            title="Tomato Recipe",
            ingredients=[(tomato, "1", "medium", False)],
        )
        await recipe_factory.create(
            title="Onion Recipe",
            ingredients=[(onion, "1", "medium", False)],
        )
        
        # Tomato is expiring, onion is not
        await pantry_factory.create(
            test_user, tomato,
            expiration_date=date.today() + timedelta(days=3),
        )
        await pantry_factory.create(test_user, onion)
        
        matches = await get_recipe_recommendations(
            db_session, test_user.id, prioritize_expiring=True
        )
        
        assert len(matches) == 2
        # Recipe using expiring tomato should be first
        assert matches[0].title == "Tomato Recipe"
        assert matches[0].uses_expiring_ingredients == 1


class TestShoppingList:
    """Unit tests for shopping list generation."""

    async def test_shopping_list_missing_items(
        self,
        db_session: AsyncSession,
        test_user: User,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test shopping list shows missing ingredients."""
        tomato = await ingredient_factory.create(name="Tomato")
        onion = await ingredient_factory.create(name="Onion")
        garlic = await ingredient_factory.create(name="Garlic")
        
        recipe = await recipe_factory.create(
            title="Test Recipe",
            ingredients=[
                (tomato, "2", "medium", False),
                (onion, "1", "large", False),
                (garlic, "3", "cloves", True),  # Optional
            ],
        )
        
        # User only has tomato
        await pantry_factory.create(test_user, tomato)
        
        shopping_list = await get_shopping_list(db_session, test_user.id, recipe.id)
        
        assert shopping_list is not None
        assert shopping_list.recipe_id == recipe.id
        assert shopping_list.total_missing == 2  # onion and garlic
        
        missing_names = [item.ingredient.name for item in shopping_list.missing_items]
        assert "Onion" in missing_names
        assert "Garlic" in missing_names  # Optional items included in shopping list

    async def test_shopping_list_recipe_not_found(
        self, db_session: AsyncSession, test_user: User
    ):
        """Test shopping list returns None for non-existent recipe."""
        shopping_list = await get_shopping_list(db_session, test_user.id, 9999)
        assert shopping_list is None


# =============================================================================
# INTEGRATION TESTS FOR ENDPOINTS
# =============================================================================

class TestRecommendationsEndpoint:
    """Integration tests for GET /recommendations."""

    async def test_get_recommendations(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        sample_ingredients: list[Ingredient],
        sample_recipe: Recipe,
        sample_pantry: list,
    ):
        """Test getting recipe recommendations."""
        response = await client.get("/recommendations/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        # Each recommendation should have required fields
        for rec in data:
            assert "id" in rec
            assert "title" in rec
            assert "match_percentage" in rec
            assert "matched_ingredients" in rec
            assert "total_required_ingredients" in rec
            assert "missing_ingredients" in rec

    async def test_get_recommendations_empty_pantry(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test recommendations with empty pantry."""
        response = await client.get("/recommendations/", headers=auth_headers)
        
        assert response.status_code == 200
        # Should return recipes but with 0% match

    async def test_get_recommendations_with_filters(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test recommendations with various filters."""
        tomato = await ingredient_factory.create(name="Tomato", is_vegan=True)
        await pantry_factory.create(test_user, tomato)
        
        await recipe_factory.create(
            title="Easy Tomato Salad",
            difficulty_level="easy",
            prep_time=5,
            cook_time=0,
            ingredients=[(tomato, "2", "medium", False)],
        )
        
        response = await client.get(
            "/recommendations/",
            headers=auth_headers,
            params={
                "min_match_percent": 50,
                "difficulty": "easy",
                "max_total_time": 30,
                "vegan": True,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_recommendations_unauthorized(self, client: AsyncClient):
        """Test recommendations without auth fails."""
        response = await client.get("/recommendations/")
        
        assert response.status_code == 401


class TestShoppingListEndpoint:
    """Integration tests for GET /recommendations/{recipe_id}/shopping-list."""

    async def test_get_shopping_list(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        sample_recipe: Recipe,
        sample_pantry: list,
    ):
        """Test getting shopping list for a recipe."""
        response = await client.get(
            f"/recommendations/{sample_recipe.id}/shopping-list",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["recipe_id"] == sample_recipe.id
        assert data["recipe_title"] == sample_recipe.title
        assert "missing_items" in data
        assert "total_missing" in data

    async def test_get_shopping_list_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test shopping list for non-existent recipe."""
        response = await client.get(
            "/recommendations/9999/shopping-list",
            headers=auth_headers,
        )
        
        assert response.status_code == 404
