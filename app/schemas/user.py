"""Pydantic schemas for User model."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for User with common fields."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    """Schema for creating a new user (registration)."""

    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=100)


class UserRead(UserBase):
    """Schema for reading user data (response)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
