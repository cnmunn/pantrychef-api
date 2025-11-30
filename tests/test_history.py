"""Tests for cooking history endpoints."""

import pytest
from httpx import AsyncClient

from app.models.cooking_history import CookingHistory
from app.models.recipe import Recipe
from app.models.user import User
from tests.conftest import (
    CookingHistoryFactory,
    RecipeFactory,
    UserFactory,
    get_auth_headers,
)


class TestListHistory:
    """Tests for GET /history."""

    async def test_list_history_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test listing history when empty."""
        response = await client.get("/history/", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_history(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
        history_factory: CookingHistoryFactory,
    ):
        """Test listing cooking history."""
        recipe = await recipe_factory.create(title="Test Recipe")
        
        await history_factory.create(test_user, recipe, rating=5)
        await history_factory.create(test_user, recipe, rating=4)
        
        response = await client.get("/history/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_list_history_unauthorized(self, client: AsyncClient):
        """Test listing history without auth fails."""
        response = await client.get("/history/")
        
        assert response.status_code == 401

    async def test_history_isolated_per_user(
        self,
        client: AsyncClient,
        user_factory: UserFactory,
        recipe_factory: RecipeFactory,
        history_factory: CookingHistoryFactory,
    ):
        """Test users only see their own history."""
        user1 = await user_factory.create()
        user2 = await user_factory.create()
        recipe = await recipe_factory.create()
        
        await history_factory.create(user1, recipe)
        
        headers = get_auth_headers(user2)
        response = await client.get("/history/", headers=headers)
        
        assert response.status_code == 200
        assert response.json() == []


class TestLogCookedRecipe:
    """Tests for POST /history."""

    async def test_log_cooked_recipe_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
    ):
        """Test logging a cooked recipe."""
        recipe = await recipe_factory.create(title="Cooked Recipe")
        
        response = await client.post(
            "/history/",
            headers=auth_headers,
            json={
                "recipe_id": recipe.id,
                "rating": 5,
                "notes": "It was delicious!",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["recipe"]["id"] == recipe.id
        assert data["rating"] == 5
        assert data["notes"] == "It was delicious!"
        assert "cooked_at" in data

    async def test_log_cooked_recipe_without_rating(
        self,
        client: AsyncClient,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
    ):
        """Test logging a cooked recipe without rating."""
        recipe = await recipe_factory.create()
        
        response = await client.post(
            "/history/",
            headers=auth_headers,
            json={"recipe_id": recipe.id},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] is None
        assert data["notes"] is None

    async def test_log_cooked_recipe_multiple_times(
        self,
        client: AsyncClient,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
    ):
        """Test logging the same recipe multiple times (allowed)."""
        recipe = await recipe_factory.create()
        
        # Log first time
        response1 = await client.post(
            "/history/",
            headers=auth_headers,
            json={"recipe_id": recipe.id, "rating": 4},
        )
        assert response1.status_code == 201
        
        # Log second time
        response2 = await client.post(
            "/history/",
            headers=auth_headers,
            json={"recipe_id": recipe.id, "rating": 5},
        )
        assert response2.status_code == 201
        
        # Verify both entries exist
        list_response = await client.get("/history/", headers=auth_headers)
        assert len(list_response.json()) == 2

    async def test_log_cooked_recipe_invalid_rating(
        self,
        client: AsyncClient,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
    ):
        """Test logging with invalid rating fails."""
        recipe = await recipe_factory.create()
        
        # Rating too high
        response = await client.post(
            "/history/",
            headers=auth_headers,
            json={"recipe_id": recipe.id, "rating": 10},
        )
        assert response.status_code == 422
        
        # Rating too low
        response = await client.post(
            "/history/",
            headers=auth_headers,
            json={"recipe_id": recipe.id, "rating": 0},
        )
        assert response.status_code == 422

    async def test_log_cooked_recipe_nonexistent(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test logging non-existent recipe fails."""
        response = await client.post(
            "/history/",
            headers=auth_headers,
            json={"recipe_id": 9999},
        )
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]


class TestCookingStats:
    """Tests for GET /history/stats."""

    async def test_stats_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test stats with no cooking history."""
        response = await client.get("/history/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_recipes_cooked"] == 0
        assert data["unique_recipes_cooked"] == 0
        assert data["average_rating"] is None

    async def test_stats_with_history(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
        history_factory: CookingHistoryFactory,
    ):
        """Test cooking statistics calculation."""
        recipe1 = await recipe_factory.create(title="Recipe 1")
        recipe2 = await recipe_factory.create(title="Recipe 2")
        
        # Cook recipe1 twice, recipe2 once
        await history_factory.create(test_user, recipe1, rating=5)
        await history_factory.create(test_user, recipe1, rating=4)
        await history_factory.create(test_user, recipe2, rating=3)
        
        response = await client.get("/history/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_recipes_cooked"] == 3
        assert data["unique_recipes_cooked"] == 2
        assert data["average_rating"] == pytest.approx(4.0, abs=0.1)  # (5+4+3)/3

    async def test_stats_with_unrated_recipes(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
        history_factory: CookingHistoryFactory,
    ):
        """Test stats excludes unrated recipes from average."""
        recipe = await recipe_factory.create()
        
        await history_factory.create(test_user, recipe, rating=5)
        await history_factory.create(test_user, recipe, rating=None)  # No rating
        
        response = await client.get("/history/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_recipes_cooked"] == 2
        assert data["average_rating"] == 5.0  # Only rated entry

    async def test_stats_most_cooked_recipe(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
        history_factory: CookingHistoryFactory,
    ):
        """Test stats includes most cooked recipe."""
        recipe1 = await recipe_factory.create(title="Frequently Made")
        recipe2 = await recipe_factory.create(title="Rarely Made")
        
        # Cook recipe1 three times, recipe2 once
        await history_factory.create(test_user, recipe1)
        await history_factory.create(test_user, recipe1)
        await history_factory.create(test_user, recipe1)
        await history_factory.create(test_user, recipe2)
        
        response = await client.get("/history/stats", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["most_cooked_recipe"] is not None
        assert data["most_cooked_recipe"]["title"] == "Frequently Made"
        assert data["most_cooked_count"] == 3

    async def test_stats_unauthorized(self, client: AsyncClient):
        """Test getting stats without auth fails."""
        response = await client.get("/history/stats")
        
        assert response.status_code == 401
