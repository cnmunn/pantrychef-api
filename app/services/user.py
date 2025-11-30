"""User service for database operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils import hash_password


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Get a user by their ID.

    Args:
        db: Database session.
        user_id: User ID to look up.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get a user by their email address.

    Args:
        db: Database session.
        email: Email address to look up.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """Get a user by their username.

    Args:
        db: Database session.
        username: Username to look up.

    Returns:
        User object if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user in the database.

    Args:
        db: Database session.
        user_data: User creation data.

    Returns:
        Created User object.
    """
    hashed_pw = hash_password(user_data.password)

    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_pw,
    )

    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user
