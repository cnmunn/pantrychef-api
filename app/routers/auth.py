"""Authentication router for user registration, login, and profile."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import Token, UserCreate, UserRead
from app.services.user import create_user, get_user_by_email, get_user_by_username
from app.utils.auth import create_access_token, verify_password
from app.utils.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Email or username already registered"},
    },
)
async def register(user_data: UserCreate, db: DbSession) -> UserRead:
    """Register a new user account.

    Creates a new user with the provided email, username, and password.
    The password is securely hashed before storage.

    - **email**: Valid email address (must be unique)
    - **username**: Unique username (3-100 characters)
    - **password**: Password (minimum 8 characters)
    """
    # Check if email already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    user = await create_user(db, user_data)
    return UserRead.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login and get access token",
    responses={
        200: {"description": "Login successful, returns JWT token"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    """Authenticate user and return a JWT access token.

    Uses OAuth2 password flow. Send credentials as form data:
    - **username**: Your email address
    - **password**: Your password

    Returns a bearer token to use in the Authorization header for protected endpoints.
    """
    # OAuth2PasswordRequestForm uses 'username' field, but we accept email
    user = await get_user_by_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user ID as subject
    access_token = create_access_token(data={"sub": str(user.id)})

    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current user profile",
    responses={
        200: {"description": "Current user profile"},
        401: {"description": "Not authenticated"},
    },
)
async def get_me(current_user: CurrentUser) -> UserRead:
    """Get the profile of the currently authenticated user.

    Requires a valid JWT token in the Authorization header:
    `Authorization: Bearer <token>`
    """
    return UserRead.model_validate(current_user)
