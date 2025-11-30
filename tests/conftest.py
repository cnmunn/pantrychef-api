"""Pytest configuration and fixtures for PantryChef API tests."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from datetime import date, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.cooking_history import CookingHistory
from app.models.favorite import Favorite
from app.models.ingredient import Ingredient
from app.models.pantry import PantryItem
from app.models.recipe import Recipe, RecipeIngredient
from app.models.user import User
from app.utils.auth import create_access_token, hash_password


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

# Use SQLite for testing (in-memory, fast)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def engine():
    """Create async test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for tests."""
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden database dependency."""
    
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


# =============================================================================
# FACTORY FIXTURES
# =============================================================================

class UserFactory:
    """Factory for creating test users."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._counter = 0
    
    async def create(
        self,
        email: str | None = None,
        username: str | None = None,
        password: str = "testpassword123",
    ) -> User:
        """Create a test user."""
        self._counter += 1
        
        user = User(
            email=email or f"test{self._counter}@example.com",
            username=username or f"testuser{self._counter}",
            hashed_password=hash_password(password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user


class IngredientFactory:
    """Factory for creating test ingredients."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._counter = 0
    
    async def create(
        self,
        name: str | None = None,
        category: str = "produce",
        is_vegetarian: bool = True,
        is_vegan: bool = True,
        is_gluten_free: bool = True,
        allergens: str | None = None,
    ) -> Ingredient:
        """Create a test ingredient."""
        self._counter += 1
        
        ingredient = Ingredient(
            name=name or f"Test Ingredient {self._counter}",
            category=category,
            is_vegetarian=is_vegetarian,
            is_vegan=is_vegan,
            is_gluten_free=is_gluten_free,
            allergens=allergens,
        )
        self.db.add(ingredient)
        await self.db.flush()
        await self.db.refresh(ingredient)
        return ingredient
    
    async def create_many(self, count: int, **kwargs) -> list[Ingredient]:
        """Create multiple test ingredients."""
        return [await self.create(**kwargs) for _ in range(count)]


class RecipeFactory:
    """Factory for creating test recipes."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._counter = 0
    
    async def create(
        self,
        title: str | None = None,
        description: str | None = None,
        instructions: str = "Test instructions",
        prep_time: int | None = 15,
        cook_time: int | None = 30,
        difficulty_level: str | None = "easy",
        servings: int | None = 4,
        ingredients: list[tuple[Ingredient, str, str, bool]] | None = None,
    ) -> Recipe:
        """Create a test recipe.
        
        Args:
            title: Recipe title.
            description: Recipe description.
            instructions: Cooking instructions.
            prep_time: Prep time in minutes.
            cook_time: Cook time in minutes.
            difficulty_level: easy, medium, or hard.
            servings: Number of servings.
            ingredients: List of tuples (ingredient, quantity, unit, optional).
        """
        self._counter += 1
        
        recipe = Recipe(
            title=title or f"Test Recipe {self._counter}",
            description=description or f"Description for recipe {self._counter}",
            instructions=instructions,
            prep_time=prep_time,
            cook_time=cook_time,
            difficulty_level=difficulty_level,
            servings=servings,
        )
        self.db.add(recipe)
        await self.db.flush()
        
        # Add ingredients if provided
        if ingredients:
            for ing, qty, unit, optional in ingredients:
                ri = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ing.id,
                    quantity=qty,
                    unit=unit,
                    optional=optional,
                )
                self.db.add(ri)
        
        await self.db.flush()
        await self.db.refresh(recipe)
        return recipe


class PantryItemFactory:
    """Factory for creating test pantry items."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user: User,
        ingredient: Ingredient,
        quantity: str | None = "1",
        unit: str | None = "unit",
        expiration_date: date | None = None,
    ) -> PantryItem:
        """Create a test pantry item."""
        item = PantryItem(
            user_id=user.id,
            ingredient_id=ingredient.id,
            quantity=quantity,
            unit=unit,
            expiration_date=expiration_date,
        )
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return item


class FavoriteFactory:
    """Factory for creating test favorites."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, user: User, recipe: Recipe) -> Favorite:
        """Create a test favorite."""
        favorite = Favorite(
            user_id=user.id,
            recipe_id=recipe.id,
        )
        self.db.add(favorite)
        await self.db.flush()
        await self.db.refresh(favorite)
        return favorite


class CookingHistoryFactory:
    """Factory for creating test cooking history entries."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(
        self,
        user: User,
        recipe: Recipe,
        rating: int | None = None,
        notes: str | None = None,
    ) -> CookingHistory:
        """Create a test cooking history entry."""
        entry = CookingHistory(
            user_id=user.id,
            recipe_id=recipe.id,
            rating=rating,
            notes=notes,
        )
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        return entry


@pytest.fixture
def user_factory(db_session: AsyncSession) -> UserFactory:
    """User factory fixture."""
    return UserFactory(db_session)


@pytest.fixture
def ingredient_factory(db_session: AsyncSession) -> IngredientFactory:
    """Ingredient factory fixture."""
    return IngredientFactory(db_session)


@pytest.fixture
def recipe_factory(db_session: AsyncSession) -> RecipeFactory:
    """Recipe factory fixture."""
    return RecipeFactory(db_session)


@pytest.fixture
def pantry_factory(db_session: AsyncSession) -> PantryItemFactory:
    """Pantry item factory fixture."""
    return PantryItemFactory(db_session)


@pytest.fixture
def favorite_factory(db_session: AsyncSession) -> FavoriteFactory:
    """Favorite factory fixture."""
    return FavoriteFactory(db_session)


@pytest.fixture
def history_factory(db_session: AsyncSession) -> CookingHistoryFactory:
    """Cooking history factory fixture."""
    return CookingHistoryFactory(db_session)


# =============================================================================
# AUTH HELPERS
# =============================================================================

def get_auth_headers(user: User) -> dict[str, str]:
    """Generate authorization headers for a user."""
    token = create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_user(user_factory: UserFactory) -> User:
    """Create a test user."""
    return await user_factory.create()


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    """Get auth headers for test user."""
    return get_auth_headers(test_user)


# =============================================================================
# SAMPLE DATA FIXTURES
# =============================================================================

@pytest.fixture
async def sample_ingredients(ingredient_factory: IngredientFactory) -> list[Ingredient]:
    """Create a set of sample ingredients."""
    ingredients = [
        await ingredient_factory.create(name="Tomato", category="produce"),
        await ingredient_factory.create(name="Onion", category="produce"),
        await ingredient_factory.create(name="Garlic", category="produce"),
        await ingredient_factory.create(name="Pasta", category="grains", is_gluten_free=False, allergens="wheat"),
        await ingredient_factory.create(name="Olive Oil", category="pantry"),
        await ingredient_factory.create(name="Salt", category="spices"),
        await ingredient_factory.create(name="Chicken Breast", category="protein", is_vegetarian=False, is_vegan=False),
        await ingredient_factory.create(name="Cheese", category="dairy", is_vegan=False, allergens="dairy"),
        await ingredient_factory.create(name="Eggs", category="dairy", is_vegan=False, allergens="eggs"),
        await ingredient_factory.create(name="Rice", category="grains"),
    ]
    return ingredients


@pytest.fixture
async def sample_recipe(
    recipe_factory: RecipeFactory,
    sample_ingredients: list[Ingredient],
) -> Recipe:
    """Create a sample recipe with ingredients."""
    tomato, onion, garlic, pasta, olive_oil, salt, _, cheese, _, _ = sample_ingredients
    
    return await recipe_factory.create(
        title="Pasta Pomodoro",
        description="Simple tomato pasta",
        instructions="1. Boil pasta. 2. Make sauce. 3. Combine.",
        prep_time=10,
        cook_time=20,
        difficulty_level="easy",
        servings=4,
        ingredients=[
            (pasta, "1", "pound", False),
            (tomato, "4", "medium", False),
            (onion, "1", "medium", False),
            (garlic, "3", "cloves", False),
            (olive_oil, "2", "tbsp", False),
            (salt, "1", "tsp", False),
            (cheese, "1/2", "cup", True),  # Optional
        ],
    )


@pytest.fixture
async def sample_pantry(
    test_user: User,
    pantry_factory: PantryItemFactory,
    sample_ingredients: list[Ingredient],
) -> list[PantryItem]:
    """Create sample pantry items for test user."""
    tomato, onion, garlic, pasta, olive_oil, salt, _, _, _, rice = sample_ingredients
    
    items = [
        await pantry_factory.create(test_user, tomato, "5", "medium"),
        await pantry_factory.create(test_user, onion, "3", "medium"),
        await pantry_factory.create(test_user, garlic, "1", "head"),
        await pantry_factory.create(test_user, pasta, "2", "pounds"),
        await pantry_factory.create(test_user, olive_oil, "1", "bottle"),
        await pantry_factory.create(test_user, salt, "1", "container"),
        await pantry_factory.create(
            test_user, rice, "2", "pounds",
            expiration_date=date.today() + timedelta(days=5),  # Expiring soon
        ),
    ]
    return items
