"""FastAPI dependencies for authentication and authorization."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.services.user import get_user_by_id
from app.utils.auth import decode_access_token

# OAuth2 scheme for JWT Bearer token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Dependency to get the current authenticated user from JWT token.

    Args:
        token: JWT token from Authorization header.
        db: Database session.

    Returns:
        Authenticated User object.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Convert to int if it's a string (JWT serializes as string)
    if isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except ValueError:
            raise credentials_exception

    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


# Type alias for dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
