"""Tests for favorites endpoints."""

import pytest
from httpx import AsyncClient

from app.models.favorite import Favorite
from app.models.recipe import Recipe
from app.models.user import User
from tests.conftest import (
    FavoriteFactory,
    RecipeFactory,
    UserFactory,
    get_auth_headers,
)


class TestListFavorites:
    """Tests for GET /favorites."""

    async def test_list_favorites_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test listing favorites when none exist."""
        response = await client.get("/favorites/", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_favorites(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
        favorite_factory: FavoriteFactory,
    ):
        """Test listing user's favorite recipes."""
        recipe1 = await recipe_factory.create(title="Recipe 1")
        recipe2 = await recipe_factory.create(title="Recipe 2")
        
        await favorite_factory.create(test_user, recipe1)
        await favorite_factory.create(test_user, recipe2)
        
        response = await client.get("/favorites/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_list_favorites_unauthorized(self, client: AsyncClient):
        """Test listing favorites without auth fails."""
        response = await client.get("/favorites/")
        
        assert response.status_code == 401

    async def test_favorites_isolated_per_user(
        self,
        client: AsyncClient,
        user_factory: UserFactory,
        recipe_factory: RecipeFactory,
        favorite_factory: FavoriteFactory,
    ):
        """Test users only see their own favorites."""
        user1 = await user_factory.create()
        user2 = await user_factory.create()
        recipe = await recipe_factory.create()
        
        await favorite_factory.create(user1, recipe)
        
        headers = get_auth_headers(user2)
        response = await client.get("/favorites/", headers=headers)
        
        assert response.status_code == 200
        assert response.json() == []


class TestAddFavorite:
    """Tests for POST /favorites/{recipe_id}."""

    async def test_add_favorite_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
    ):
        """Test adding a recipe to favorites."""
        recipe = await recipe_factory.create(title="Delicious Recipe")
        
        response = await client.post(
            f"/favorites/{recipe.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["recipe"]["id"] == recipe.id
        assert data["recipe"]["title"] == "Delicious Recipe"

    async def test_add_favorite_duplicate(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
        favorite_factory: FavoriteFactory,
    ):
        """Test adding duplicate favorite fails."""
        recipe = await recipe_factory.create()
        await favorite_factory.create(test_user, recipe)
        
        response = await client.post(
            f"/favorites/{recipe.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    async def test_add_favorite_nonexistent_recipe(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test adding non-existent recipe to favorites fails."""
        response = await client.post(
            "/favorites/9999",
            headers=auth_headers,
        )
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    async def test_add_favorite_unauthorized(
        self, client: AsyncClient, recipe_factory: RecipeFactory
    ):
        """Test adding favorite without auth fails."""
        recipe = await recipe_factory.create()
        
        response = await client.post(f"/favorites/{recipe.id}")
        
        assert response.status_code == 401


class TestRemoveFavorite:
    """Tests for DELETE /favorites/{recipe_id}."""

    async def test_remove_favorite_success(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
        favorite_factory: FavoriteFactory,
    ):
        """Test removing a recipe from favorites."""
        recipe = await recipe_factory.create()
        await favorite_factory.create(test_user, recipe)
        
        response = await client.delete(
            f"/favorites/{recipe.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 200
        assert "removed" in response.json()["message"].lower()
        
        # Verify it's actually removed
        list_response = await client.get("/favorites/", headers=auth_headers)
        assert list_response.json() == []

    async def test_remove_favorite_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
        recipe_factory: RecipeFactory,
    ):
        """Test removing non-favorited recipe fails."""
        recipe = await recipe_factory.create()
        
        response = await client.delete(
            f"/favorites/{recipe.id}",
            headers=auth_headers,
        )
        
        assert response.status_code == 404

    async def test_remove_other_user_favorite(
        self,
        client: AsyncClient,
        user_factory: UserFactory,
        recipe_factory: RecipeFactory,
        favorite_factory: FavoriteFactory,
    ):
        """Test removing another user's favorite fails."""
        user1 = await user_factory.create()
        user2 = await user_factory.create()
        recipe = await recipe_factory.create()
        
        await favorite_factory.create(user1, recipe)
        
        headers = get_auth_headers(user2)
        response = await client.delete(
            f"/favorites/{recipe.id}",
            headers=headers,
        )
        
        assert response.status_code == 404
