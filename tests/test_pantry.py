"""Tests for pantry endpoints."""

from datetime import date, timedelta

import pytest
from httpx import AsyncClient

from app.models.ingredient import Ingredient
from app.models.pantry import PantryItem
from app.models.user import User
from tests.conftest import (
    IngredientFactory,
    PantryItemFactory,
    UserFactory,
    get_auth_headers,
)


class TestListPantryItems:
    """Tests for GET /pantry."""

    async def test_list_pantry_empty(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test listing pantry when empty."""
        response = await client.get("/pantry/", headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_pantry_items(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        ingredient_factory: IngredientFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test listing user's pantry items."""
        tomato = await ingredient_factory.create(name="Tomato")
        onion = await ingredient_factory.create(name="Onion")
        
        await pantry_factory.create(test_user, tomato, quantity="5", unit="medium")
        await pantry_factory.create(test_user, onion, quantity="3", unit="large")
        
        response = await client.get("/pantry/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    async def test_list_pantry_unauthorized(self, client: AsyncClient):
        """Test listing pantry without auth fails."""
        response = await client.get("/pantry/")
        
        assert response.status_code == 401

    async def test_pantry_items_isolated_per_user(
        self,
        client: AsyncClient,
        user_factory: UserFactory,
        ingredient_factory: IngredientFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test users only see their own pantry items."""
        user1 = await user_factory.create()
        user2 = await user_factory.create()
        tomato = await ingredient_factory.create(name="Tomato")
        
        await pantry_factory.create(user1, tomato)
        
        # User2 should not see user1's items
        headers = get_auth_headers(user2)
        response = await client.get("/pantry/", headers=headers)
        
        assert response.status_code == 200
        assert response.json() == []


class TestAddPantryItem:
    """Tests for POST /pantry."""

    async def test_add_pantry_item_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        ingredient_factory: IngredientFactory,
    ):
        """Test adding item to pantry."""
        ingredient = await ingredient_factory.create(name="Tomato")
        
        response = await client.post(
            "/pantry/",
            headers=auth_headers,
            json={
                "ingredient_id": ingredient.id,
                "quantity": "5",
                "unit": "medium",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["ingredient"]["id"] == ingredient.id
        assert data["quantity"] == "5"
        assert data["unit"] == "medium"

    async def test_add_pantry_item_with_expiration(
        self,
        client: AsyncClient,
        auth_headers: dict,
        ingredient_factory: IngredientFactory,
    ):
        """Test adding item with expiration date."""
        ingredient = await ingredient_factory.create(name="Milk")
        expiration = (date.today() + timedelta(days=7)).isoformat()
        
        response = await client.post(
            "/pantry/",
            headers=auth_headers,
            json={
                "ingredient_id": ingredient.id,
                "expiration_date": expiration,
            },
        )
        
        assert response.status_code == 201
        assert response.json()["expiration_date"] == expiration

    async def test_add_pantry_item_invalid_ingredient(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test adding item with invalid ingredient fails."""
        response = await client.post(
            "/pantry/",
            headers=auth_headers,
            json={"ingredient_id": 9999},
        )
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"]

    async def test_add_pantry_item_duplicate(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        ingredient_factory: IngredientFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test adding duplicate ingredient fails."""
        ingredient = await ingredient_factory.create(name="Tomato")
        await pantry_factory.create(test_user, ingredient)
        
        response = await client.post(
            "/pantry/",
            headers=auth_headers,
            json={"ingredient_id": ingredient.id},
        )
        
        assert response.status_code == 400
        assert "already in your pantry" in response.json()["detail"]


class TestBulkAddPantryItems:
    """Tests for POST /pantry/bulk."""

    async def test_bulk_add_success(
        self,
        client: AsyncClient,
        auth_headers: dict,
        ingredient_factory: IngredientFactory,
    ):
        """Test adding multiple items at once."""
        tomato = await ingredient_factory.create(name="Tomato")
        onion = await ingredient_factory.create(name="Onion")
        
        response = await client.post(
            "/pantry/bulk",
            headers=auth_headers,
            json={
                "items": [
                    {"ingredient_id": tomato.id, "quantity": "5"},
                    {"ingredient_id": onion.id, "quantity": "3"},
                ]
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 2

    async def test_bulk_add_skips_existing(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        ingredient_factory: IngredientFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test bulk add skips already existing items."""
        tomato = await ingredient_factory.create(name="Tomato")
        onion = await ingredient_factory.create(name="Onion")
        
        # Tomato already in pantry
        await pantry_factory.create(test_user, tomato)
        
        response = await client.post(
            "/pantry/bulk",
            headers=auth_headers,
            json={
                "items": [
                    {"ingredient_id": tomato.id},
                    {"ingredient_id": onion.id},
                ]
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 1  # Only onion added
        assert data[0]["ingredient"]["name"] == "Onion"


class TestUpdatePantryItem:
    """Tests for PATCH /pantry/{id}."""

    async def test_update_pantry_item(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        ingredient_factory: IngredientFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test updating a pantry item."""
        ingredient = await ingredient_factory.create(name="Tomato")
        item = await pantry_factory.create(test_user, ingredient, quantity="5", unit="medium")
        
        response = await client.patch(
            f"/pantry/{item.id}",
            headers=auth_headers,
            json={"quantity": "10", "unit": "large"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == "10"
        assert data["unit"] == "large"

    async def test_update_pantry_item_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating non-existent item fails."""
        response = await client.patch(
            "/pantry/9999",
            headers=auth_headers,
            json={"quantity": "10"},
        )
        
        assert response.status_code == 404

    async def test_update_other_user_item(
        self,
        client: AsyncClient,
        user_factory: UserFactory,
        ingredient_factory: IngredientFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test updating another user's item fails."""
        user1 = await user_factory.create()
        user2 = await user_factory.create()
        ingredient = await ingredient_factory.create()
        item = await pantry_factory.create(user1, ingredient)
        
        headers = get_auth_headers(user2)
        response = await client.patch(
            f"/pantry/{item.id}",
            headers=headers,
            json={"quantity": "10"},
        )
        
        assert response.status_code == 404


class TestDeletePantryItem:
    """Tests for DELETE /pantry/{id}."""

    async def test_delete_pantry_item(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        ingredient_factory: IngredientFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test deleting a pantry item."""
        ingredient = await ingredient_factory.create()
        item = await pantry_factory.create(test_user, ingredient)
        
        response = await client.delete(f"/pantry/{item.id}", headers=auth_headers)
        
        assert response.status_code == 200
        assert "removed" in response.json()["message"].lower()

    async def test_delete_pantry_item_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test deleting non-existent item fails."""
        response = await client.delete("/pantry/9999", headers=auth_headers)
        
        assert response.status_code == 404


class TestExpiringItems:
    """Tests for GET /pantry/expiring."""

    async def test_get_expiring_items(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        ingredient_factory: IngredientFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test getting items expiring soon."""
        tomato = await ingredient_factory.create(name="Tomato")
        milk = await ingredient_factory.create(name="Milk")
        rice = await ingredient_factory.create(name="Rice")
        
        # Expiring in 3 days
        await pantry_factory.create(
            test_user, tomato,
            expiration_date=date.today() + timedelta(days=3),
        )
        # Expiring in 10 days (outside default 7-day window)
        await pantry_factory.create(
            test_user, milk,
            expiration_date=date.today() + timedelta(days=10),
        )
        # No expiration date
        await pantry_factory.create(test_user, rice)
        
        response = await client.get("/pantry/expiring", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["ingredient"]["name"] == "Tomato"

    async def test_get_expiring_items_custom_days(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        ingredient_factory: IngredientFactory,
        pantry_factory: PantryItemFactory,
    ):
        """Test getting expiring items with custom day range."""
        milk = await ingredient_factory.create(name="Milk")
        await pantry_factory.create(
            test_user, milk,
            expiration_date=date.today() + timedelta(days=10),
        )
        
        response = await client.get(
            "/pantry/expiring",
            headers=auth_headers,
            params={"days": 14},
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 1
