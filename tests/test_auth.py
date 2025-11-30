"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient

from app.models.user import User
from tests.conftest import UserFactory, get_auth_headers


class TestRegister:
    """Tests for POST /auth/register."""

    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepassword123",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password

    async def test_register_duplicate_email(
        self, client: AsyncClient, user_factory: UserFactory
    ):
        """Test registration fails with duplicate email."""
        # Create existing user
        await user_factory.create(email="existing@example.com")
        
        response = await client.post(
            "/auth/register",
            json={
                "email": "existing@example.com",
                "username": "newuser",
                "password": "password123",
            },
        )
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    async def test_register_duplicate_username(
        self, client: AsyncClient, user_factory: UserFactory
    ):
        """Test registration fails with duplicate username."""
        await user_factory.create(username="existinguser")
        
        response = await client.post(
            "/auth/register",
            json={
                "email": "new@example.com",
                "username": "existinguser",
                "password": "password123",
            },
        )
        
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration fails with invalid email."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "not-an-email",
                "username": "validuser",
                "password": "password123",
            },
        )
        
        assert response.status_code == 422  # Validation error

    async def test_register_short_password(self, client: AsyncClient):
        """Test registration fails with short password."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "username": "validuser",
                "password": "short",  # Less than 8 characters
            },
        )
        
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /auth/login."""

    async def test_login_success(
        self, client: AsyncClient, user_factory: UserFactory
    ):
        """Test successful login returns token."""
        password = "testpassword123"
        user = await user_factory.create(
            email="login@example.com",
            password=password,
        )
        
        response = await client.post(
            "/auth/login",
            data={
                "username": user.email,  # OAuth2 uses 'username' field
                "password": password,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(
        self, client: AsyncClient, user_factory: UserFactory
    ):
        """Test login fails with wrong password."""
        user = await user_factory.create(password="correctpassword")
        
        response = await client.post(
            "/auth/login",
            data={
                "username": user.email,
                "password": "wrongpassword",
            },
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login fails for non-existent user."""
        response = await client.post(
            "/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "anypassword",
            },
        )
        
        assert response.status_code == 401


class TestGetMe:
    """Tests for GET /auth/me."""

    async def test_get_me_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test getting current user profile."""
        response = await client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username

    async def test_get_me_unauthorized(self, client: AsyncClient):
        """Test getting profile without auth fails."""
        response = await client.get("/auth/me")
        
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test getting profile with invalid token fails."""
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        
        assert response.status_code == 401
