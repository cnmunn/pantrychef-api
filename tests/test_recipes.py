"""Tests for recipes endpoints."""

import pytest
from httpx import AsyncClient

from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from tests.conftest import IngredientFactory, RecipeFactory


class TestListRecipes:
    """Tests for GET /recipes."""

    async def test_list_recipes_empty(self, client: AsyncClient):
        """Test listing recipes when none exist."""
        response = await client.get("/recipes/")
        
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_recipes(
        self, client: AsyncClient, recipe_factory: RecipeFactory
    ):
        """Test listing all recipes."""
        await recipe_factory.create(title="Recipe A")
        await recipe_factory.create(title="Recipe B")
        
        response = await client.get("/recipes/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_list_recipes_filter_by_difficulty(
        self, client: AsyncClient, recipe_factory: RecipeFactory
    ):
        """Test filtering recipes by difficulty."""
        await recipe_factory.create(title="Easy Recipe", difficulty_level="easy")
        await recipe_factory.create(title="Hard Recipe", difficulty_level="hard")
        
        response = await client.get("/recipes/", params={"difficulty": "easy"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Easy Recipe"

    async def test_list_recipes_filter_by_time(
        self, client: AsyncClient, recipe_factory: RecipeFactory
    ):
        """Test filtering recipes by maximum prep/cook time."""
        await recipe_factory.create(title="Quick Recipe", prep_time=5, cook_time=10)
        await recipe_factory.create(title="Slow Recipe", prep_time=30, cook_time=60)
        
        # Filter by max prep time
        response = await client.get("/recipes/", params={"max_prep_time": 10})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Quick Recipe"
        
        # Filter by max cook time
        response = await client.get("/recipes/", params={"max_cook_time": 20})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Quick Recipe"

    async def test_list_recipes_pagination(
        self, client: AsyncClient, recipe_factory: RecipeFactory
    ):
        """Test pagination of recipes."""
        for i in range(10):
            await recipe_factory.create(title=f"Recipe {i}")
        
        response = await client.get("/recipes/", params={"skip": 0, "limit": 5})
        assert response.status_code == 200
        assert len(response.json()) == 5
        
        response = await client.get("/recipes/", params={"skip": 5, "limit": 5})
        assert response.status_code == 200
        assert len(response.json()) == 5


class TestGetRecipe:
    """Tests for GET /recipes/{id}."""

    async def test_get_recipe_success(
        self,
        client: AsyncClient,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
    ):
        """Test getting a single recipe with ingredients."""
        tomato = await ingredient_factory.create(name="Tomato")
        onion = await ingredient_factory.create(name="Onion")
        
        recipe = await recipe_factory.create(
            title="Test Recipe",
            description="A test recipe",
            prep_time=15,
            cook_time=30,
            difficulty_level="medium",
            servings=4,
            ingredients=[
                (tomato, "2", "medium", False),
                (onion, "1", "large", True),
            ],
        )
        
        response = await client.get(f"/recipes/{recipe.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == recipe.id
        assert data["title"] == "Test Recipe"
        assert data["description"] == "A test recipe"
        assert data["prep_time"] == 15
        assert data["cook_time"] == 30
        assert data["difficulty_level"] == "medium"
        assert data["servings"] == 4
        assert len(data["recipe_ingredients"]) == 2

    async def test_get_recipe_includes_ingredient_details(
        self,
        client: AsyncClient,
        ingredient_factory: IngredientFactory,
        recipe_factory: RecipeFactory,
    ):
        """Test recipe response includes full ingredient details."""
        tomato = await ingredient_factory.create(
            name="Tomato",
            category="produce",
            is_vegetarian=True,
            is_vegan=True,
        )
        
        recipe = await recipe_factory.create(
            title="Tomato Recipe",
            ingredients=[(tomato, "2", "medium", False)],
        )
        
        response = await client.get(f"/recipes/{recipe.id}")
        
        assert response.status_code == 200
        data = response.json()
        ri = data["recipe_ingredients"][0]
        assert ri["quantity"] == "2"
        assert ri["unit"] == "medium"
        assert ri["optional"] is False
        assert ri["ingredient"]["name"] == "Tomato"
        assert ri["ingredient"]["category"] == "produce"

    async def test_get_recipe_not_found(self, client: AsyncClient):
        """Test getting non-existent recipe returns 404."""
        response = await client.get("/recipes/9999")
        
        assert response.status_code == 404


class TestCreateRecipe:
    """Tests for POST /recipes."""

    async def test_create_recipe_success(
        self, client: AsyncClient, ingredient_factory: IngredientFactory
    ):
        """Test creating a new recipe."""
        tomato = await ingredient_factory.create(name="Tomato")
        onion = await ingredient_factory.create(name="Onion")
        
        response = await client.post(
            "/recipes/",
            json={
                "title": "New Recipe",
                "description": "A delicious new recipe",
                "instructions": "Step 1: Prep. Step 2: Cook. Step 3: Serve.",
                "prep_time": 15,
                "cook_time": 30,
                "difficulty_level": "easy",
                "servings": 4,
                "ingredients": [
                    {"ingredient_id": tomato.id, "quantity": "2", "unit": "medium", "optional": False},
                    {"ingredient_id": onion.id, "quantity": "1", "unit": "large", "optional": True},
                ],
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Recipe"
        assert data["description"] == "A delicious new recipe"
        assert "id" in data

    async def test_create_recipe_minimal(
        self, client: AsyncClient, ingredient_factory: IngredientFactory
    ):
        """Test creating recipe with minimal required fields."""
        ingredient = await ingredient_factory.create(name="Salt")
        
        response = await client.post(
            "/recipes/",
            json={
                "title": "Minimal Recipe",
                "instructions": "Just add salt to water.",
                "ingredients": [
                    {"ingredient_id": ingredient.id},
                ],
            },
        )
        
        assert response.status_code == 201

    async def test_create_recipe_invalid_ingredient(self, client: AsyncClient):
        """Test creating recipe with non-existent ingredient fails."""
        response = await client.post(
            "/recipes/",
            json={
                "title": "Bad Recipe",
                "instructions": "This won't work.",
                "ingredients": [
                    {"ingredient_id": 9999, "quantity": "1", "unit": "unit"},
                ],
            },
        )
        
        assert response.status_code == 400

    async def test_create_recipe_no_ingredients(self, client: AsyncClient):
        """Test creating recipe without ingredients fails."""
        response = await client.post(
            "/recipes/",
            json={
                "title": "Empty Recipe",
                "instructions": "Nothing to do.",
                "ingredients": [],
            },
        )
        
        assert response.status_code == 422  # Validation error

    async def test_create_recipe_invalid_difficulty(
        self, client: AsyncClient, ingredient_factory: IngredientFactory
    ):
        """Test creating recipe with invalid difficulty level fails."""
        ingredient = await ingredient_factory.create()
        
        response = await client.post(
            "/recipes/",
            json={
                "title": "Recipe",
                "instructions": "Do stuff.",
                "difficulty_level": "impossible",  # Invalid
                "ingredients": [{"ingredient_id": ingredient.id}],
            },
        )
        
        assert response.status_code == 422


class TestSearchRecipes:
    """Tests for GET /recipes/search."""

    async def test_search_recipes_by_title(
        self, client: AsyncClient, recipe_factory: RecipeFactory
    ):
        """Test searching recipes by title."""
        await recipe_factory.create(title="Chicken Pasta")
        await recipe_factory.create(title="Beef Stew")
        await recipe_factory.create(title="Pasta Salad")
        
        response = await client.get("/recipes/search", params={"q": "pasta"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        titles = [r["title"] for r in data]
        assert "Chicken Pasta" in titles
        assert "Pasta Salad" in titles

    async def test_search_recipes_by_description(
        self, client: AsyncClient, recipe_factory: RecipeFactory
    ):
        """Test searching recipes by description."""
        await recipe_factory.create(
            title="Recipe A",
            description="A healthy vegetarian meal"
        )
        await recipe_factory.create(
            title="Recipe B",
            description="A hearty meat dish"
        )
        
        response = await client.get("/recipes/search", params={"q": "vegetarian"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Recipe A"

    async def test_search_recipes_case_insensitive(
        self, client: AsyncClient, recipe_factory: RecipeFactory
    ):
        """Test search is case-insensitive."""
        await recipe_factory.create(title="CHICKEN SOUP")
        
        response = await client.get("/recipes/search", params={"q": "chicken"})
        
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_search_recipes_no_results(
        self, client: AsyncClient, recipe_factory: RecipeFactory
    ):
        """Test search with no matching results."""
        await recipe_factory.create(title="Tomato Soup")
        
        response = await client.get("/recipes/search", params={"q": "xyz123"})
        
        assert response.status_code == 200
        assert response.json() == []
