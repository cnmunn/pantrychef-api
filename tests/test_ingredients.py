"""Tests for ingredients endpoints."""

import pytest
from httpx import AsyncClient

from app.models.ingredient import Ingredient
from tests.conftest import IngredientFactory


class TestListIngredients:
    """Tests for GET /ingredients."""

    async def test_list_ingredients_empty(self, client: AsyncClient):
        """Test listing ingredients when none exist."""
        response = await client.get("/ingredients/")
        
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_ingredients(
        self, client: AsyncClient, ingredient_factory: IngredientFactory
    ):
        """Test listing all ingredients."""
        await ingredient_factory.create(name="Tomato", category="produce")
        await ingredient_factory.create(name="Milk", category="dairy")
        
        response = await client.get("/ingredients/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [ing["name"] for ing in data]
        assert "Tomato" in names
        assert "Milk" in names

    async def test_list_ingredients_filter_by_category(
        self, client: AsyncClient, ingredient_factory: IngredientFactory
    ):
        """Test filtering ingredients by category."""
        await ingredient_factory.create(name="Tomato", category="produce")
        await ingredient_factory.create(name="Carrot", category="produce")
        await ingredient_factory.create(name="Milk", category="dairy")
        
        response = await client.get("/ingredients/", params={"category": "produce"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for ing in data:
            assert ing["category"] == "produce"

    async def test_list_ingredients_pagination(
        self, client: AsyncClient, ingredient_factory: IngredientFactory
    ):
        """Test pagination of ingredients."""
        await ingredient_factory.create_many(10)
        
        # First page
        response = await client.get("/ingredients/", params={"skip": 0, "limit": 5})
        assert response.status_code == 200
        assert len(response.json()) == 5
        
        # Second page
        response = await client.get("/ingredients/", params={"skip": 5, "limit": 5})
        assert response.status_code == 200
        assert len(response.json()) == 5


class TestGetIngredient:
    """Tests for GET /ingredients/{id}."""

    async def test_get_ingredient_success(
        self, client: AsyncClient, ingredient_factory: IngredientFactory
    ):
        """Test getting a single ingredient."""
        ingredient = await ingredient_factory.create(
            name="Garlic",
            category="produce",
            is_vegetarian=True,
            is_vegan=True,
            is_gluten_free=True,
        )
        
        response = await client.get(f"/ingredients/{ingredient.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ingredient.id
        assert data["name"] == "Garlic"
        assert data["category"] == "produce"
        assert data["is_vegetarian"] is True
        assert data["is_vegan"] is True
        assert data["is_gluten_free"] is True

    async def test_get_ingredient_not_found(self, client: AsyncClient):
        """Test getting non-existent ingredient returns 404."""
        response = await client.get("/ingredients/9999")
        
        assert response.status_code == 404


class TestCreateIngredient:
    """Tests for POST /ingredients."""

    async def test_create_ingredient_success(self, client: AsyncClient):
        """Test creating a new ingredient."""
        response = await client.post(
            "/ingredients/",
            json={
                "name": "New Ingredient",
                "category": "produce",
                "is_vegetarian": True,
                "is_vegan": True,
                "is_gluten_free": True,
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Ingredient"
        assert data["category"] == "produce"
        assert "id" in data

    async def test_create_ingredient_with_allergens(self, client: AsyncClient):
        """Test creating ingredient with allergen info."""
        response = await client.post(
            "/ingredients/",
            json={
                "name": "Peanuts",
                "category": "nuts",
                "is_vegetarian": True,
                "is_vegan": True,
                "is_gluten_free": True,
                "allergens": "peanuts,nuts",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["allergens"] == "peanuts,nuts"

    async def test_create_ingredient_non_vegan(self, client: AsyncClient):
        """Test creating a non-vegan ingredient."""
        response = await client.post(
            "/ingredients/",
            json={
                "name": "Beef",
                "category": "protein",
                "is_vegetarian": False,
                "is_vegan": False,
                "is_gluten_free": True,
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["is_vegetarian"] is False
        assert data["is_vegan"] is False

    async def test_create_ingredient_duplicate_name(
        self, client: AsyncClient, ingredient_factory: IngredientFactory
    ):
        """Test creating ingredient with duplicate name fails."""
        await ingredient_factory.create(name="Existing Ingredient")
        
        response = await client.post(
            "/ingredients/",
            json={
                "name": "Existing Ingredient",
                "category": "produce",
            },
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestListCategories:
    """Tests for GET /ingredients/categories."""

    async def test_list_categories(
        self, client: AsyncClient, ingredient_factory: IngredientFactory
    ):
        """Test listing all unique categories."""
        await ingredient_factory.create(category="produce")
        await ingredient_factory.create(category="produce")  # Duplicate
        await ingredient_factory.create(category="dairy")
        await ingredient_factory.create(category="protein")
        
        response = await client.get("/ingredients/categories")
        
        assert response.status_code == 200
        categories = response.json()
        assert len(categories) == 3
        assert "produce" in categories
        assert "dairy" in categories
        assert "protein" in categories
