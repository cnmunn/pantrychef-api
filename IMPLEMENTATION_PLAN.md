# 🍳 PantryChef API - Implementation Plan

> A FastAPI-powered recipe recommendation service that suggests meals based on ingredients you have at home

## Overview

**PantryChef** is a RESTful API that helps users discover recipes based on ingredients they already have in their kitchen. Users can manage their pantry inventory, get smart recipe suggestions ranked by ingredient match percentage, save favorite recipes, and track what they've cooked.

---

## Why This Project?

- **Practical utility**: Solves a real problem (reducing food waste, meal planning)
- **Rich domain model**: Users, ingredients, recipes, favorites, cooking history
- **Interesting algorithms**: Ingredient matching, ranking, dietary filtering
- **Scalable complexity**: Can start simple, expand to ML recommendations
- **API design showcase**: Demonstrates filtering, pagination, nested resources

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Package Manager | uv |
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) |
| Testing | pytest + httpx |
| Documentation | OpenAPI (auto-generated) |

---

## Phase 1: Project Foundation ✅

### Step 1.1 - Initialize Project with uv
- [x] Initialize uv in current directory:
  ```bash
  uv init
  ```
- [x] Set Python version (3.11+):
  ```bash
  uv python pin 3.12
  ```
- [x] Add core dependencies:
  ```bash
  uv add fastapi uvicorn[standard] sqlalchemy[asyncio] asyncpg alembic
  uv add pydantic pydantic-settings python-jose[cryptography] passlib[bcrypt]
  ```
- [x] Add dev dependencies:
  ```bash
  uv add --dev pytest pytest-asyncio pytest-cov httpx ruff mypy
  ```

### Step 1.2 - Project Structure Setup
- [x] Create directory structure:
  ```
  stl-test/
  ├── pyproject.toml           # Managed by uv
  ├── uv.lock                  # Lock file (auto-generated)
  ├── .python-version          # Python version pin
  ├── IMPLEMENTATION_PLAN.md   # This file
  ├── app/
  │   ├── __init__.py
  │   ├── main.py              # FastAPI app instance
  │   ├── config.py            # Settings/environment
  │   ├── database.py          # DB connection
  │   ├── models/              # SQLAlchemy models
  │   ├── schemas/             # Pydantic schemas
  │   ├── routers/             # API route handlers
  │   ├── services/            # Business logic
  │   └── utils/               # Helpers
  ├── alembic/                 # Migrations
  ├── scripts/                 # Utility scripts (seed, etc.)
  ├── tests/
  ├── .env.example             # Environment template
  └── README.md
  ```

### Step 1.3 - Configuration Management
- [x] Create settings class using Pydantic `BaseSettings`
- [x] Support `.env` file for local development
- [x] Define configs: DATABASE_URL, SECRET_KEY, JWT settings

### Step 1.4 - Database Connection
- [x] Set up async SQLAlchemy engine
- [x] Create session dependency for FastAPI
- [x] Initialize Alembic for migrations:
  ```bash
  uv run alembic init alembic
  ```

### Step 1.5 - Development Scripts
- [x] Add scripts to `pyproject.toml`:
  ```toml
  [project.scripts]
  dev = "uvicorn app.main:app --reload"
  
  [tool.uv.scripts]
  dev = "uvicorn app.main:app --reload"
  test = "pytest"
  lint = "ruff check ."
  format = "ruff format ."
  migrate = "alembic upgrade head"
  ```
- [x] Verify dev server runs:
  ```bash
  uv run dev
  ```

---

## Phase 2: Data Models ✅

### Step 2.1 - Core SQLAlchemy Models

**User** ✅ (`app/models/user.py`)
- id, email, hashed_password, username, created_at
- Relationships: pantry_items, favorites, cooking_history

**Ingredient** ✅ (`app/models/ingredient.py`)
- id, name, category (produce, dairy, protein, etc.)
- Unique constraint on name

**Recipe** ✅ (`app/models/recipe.py`)
- id, title, description, instructions, prep_time, cook_time
- difficulty_level, servings, image_url, source_url
- Relationships: recipe_ingredients

**RecipeIngredient** ✅ (`app/models/recipe.py`)
- recipe_id, ingredient_id, quantity, unit, optional (bool)

**PantryItem** ✅ (`app/models/pantry.py`)
- id, user_id, ingredient_id, quantity, unit, expiration_date

**Favorite** ✅ (`app/models/favorite.py`)
- id, user_id, recipe_id, created_at

**CookingHistory** ✅ (`app/models/cooking_history.py`)
- id, user_id, recipe_id, cooked_at, rating, notes

### Step 2.2 - Create Alembic Migrations
- [x] Generate initial migration for all models:
  ```bash
  # Created manually: alembic/versions/001_initial_schema.py
  ```
- [x] Test migration up/down (requires running PostgreSQL):
  ```bash
  uv run alembic upgrade head
  uv run alembic downgrade -1
  ```

---

## Phase 3: Pydantic Schemas ✅

### Step 3.1 - Request/Response Schemas
- [x] `UserCreate`, `UserRead`, `UserUpdate` (`app/schemas/user.py`)
- [x] `IngredientCreate`, `IngredientRead` (`app/schemas/ingredient.py`)
- [x] `RecipeCreate`, `RecipeRead`, `RecipeSummary`, `RecipeIngredientCreate`, `RecipeIngredientRead` (`app/schemas/recipe.py`)
- [x] `PantryItemCreate`, `PantryItemRead`, `PantryItemUpdate`, `PantryItemBulkCreate` (`app/schemas/pantry.py`)
- [x] `FavoriteRead` (`app/schemas/favorite.py`)
- [x] `CookingHistoryCreate`, `CookingHistoryRead`, `CookingStats` (`app/schemas/cooking_history.py`)

### Step 3.2 - Special Response Schemas
- [x] `RecipeMatch` - includes match_percentage, matched/missing ingredients (`app/schemas/common.py`)
- [x] `PaginatedResponse[T]` - generic pagination wrapper with has_next/has_prev (`app/schemas/common.py`)
- [x] `Token`, `TokenData` - JWT access token response and data (`app/schemas/common.py`)
- [x] `ShoppingList`, `ShoppingListItem` - missing ingredients for a recipe (`app/schemas/common.py`)
- [x] `Message` - simple message response (`app/schemas/common.py`)

---

## Phase 4: Authentication ✅

### Step 4.1 - Auth Utilities
- [x] Password hashing with bcrypt (`app/utils/auth.py`)
- [x] JWT token creation/verification (`app/utils/auth.py`)
- [x] `get_current_user` dependency (`app/utils/dependencies.py`)
- [x] User service for database operations (`app/services/user.py`)

### Step 4.2 - Auth Endpoints
- [x] `POST /auth/register` - Create new user (`app/routers/auth.py`)
- [x] `POST /auth/login` - Return JWT token (OAuth2 password flow)
- [x] `GET /auth/me` - Get current user profile (protected)

---

## Phase 5: API Endpoints ✅

### Step 5.1 - Ingredients Router (`/ingredients`) ✅
- [x] `GET /` - List all ingredients (with category filter)
- [x] `GET /{id}` - Get single ingredient
- [x] `POST /` - Create ingredient (admin)
- [x] `GET /categories` - List all categories

**Implementation Details:**
- Created `app/services/ingredient.py` with CRUD operations and category listing
- Created `app/routers/ingredients.py` with full REST API
- Pagination support via `skip` and `limit` query parameters
- Case-insensitive category filtering

### Step 5.2 - Pantry Router (`/pantry`) ✅
- [x] `GET /` - List user's pantry items
- [x] `POST /` - Add item to pantry
- [x] `PATCH /{id}` - Update quantity/expiration
- [x] `DELETE /{id}` - Remove from pantry
- [x] `POST /bulk` - Add multiple items at once
- [x] `GET /expiring` - Get items expiring soon (bonus feature)

**Implementation Details:**
- Created `app/services/pantry.py` with full CRUD + bulk operations
- Created `app/routers/pantry.py` with protected endpoints (requires auth)
- User ownership verification on all operations
- Expiration tracking with configurable lookahead days

### Step 5.3 - Recipes Router (`/recipes`) ✅
- [x] `GET /` - List recipes (pagination, filters)
- [x] `GET /{id}` - Get recipe with full details
- [x] `POST /` - Create recipe (admin)
- [x] `GET /search` - Search by title/description

**Implementation Details:**
- Created `app/services/recipe.py` with full CRUD and search
- Created `app/routers/recipes.py` with filtering by difficulty and time
- Eager loading of recipe ingredients with relationships
- Case-insensitive search on title and description

### Step 5.4 - Recommendations Router (`/recommendations`) ✅
- [x] `GET /` - **Core feature**: Get recipes ranked by pantry match
  - Query params: `min_match_percent`, `max_missing_ingredients`, `difficulty`, `max_total_time`
  - Returns recipes sorted by match percentage
- [x] `GET /{recipe_id}/shopping-list` - Missing ingredients for a recipe

**Implementation Details:**
- Created `app/services/recommendation.py` with matching algorithm
- Algorithm calculates match % based on required (non-optional) ingredients only
- Recipes ranked by match percentage descending
- Shopping list shows all missing ingredients with quantities

### Step 5.5 - Favorites Router (`/favorites`) ✅
- [x] `GET /` - List user's favorite recipes
- [x] `POST /{recipe_id}` - Add to favorites
- [x] `DELETE /{recipe_id}` - Remove from favorites

**Implementation Details:**
- Created `app/services/favorite.py` with CRUD operations
- Created `app/routers/favorites.py` with protected endpoints
- Prevents duplicate favorites (unique constraint enforced)

### Step 5.6 - Cooking History Router (`/history`) ✅
- [x] `GET /` - List cooking history
- [x] `POST /` - Log a cooked recipe with rating
- [x] `GET /stats` - Cooking statistics (most cooked, avg rating)

**Implementation Details:**
- Created `app/services/cooking_history.py` with logging and stats
- Created `app/routers/history.py` with protected endpoints
- Stats include: total cooked, unique recipes, average rating, most cooked recipe

---

## Phase 6: Business Logic (Services Layer) ✅

### Step 6.1 - Recipe Matching Algorithm ✅
```
For each recipe:
  1. Get recipe's required ingredients (non-optional)
  2. Get user's pantry ingredients
  3. Calculate match = (matched / required) * 100
  4. Return sorted by match percentage descending
```

**Implemented in `app/services/recommendation.py`**

### Step 6.2 - Smart Filtering ✅
- [x] Filter by dietary restrictions (vegetarian, vegan, gluten-free)
- [x] Filter by max prep time
- [x] Filter by difficulty level
- [x] Filter by max total time (prep + cook)
- [x] Exclude recipes with allergen ingredients

**Implementation Details:**
- Added dietary flags to Ingredient model: `is_vegetarian`, `is_vegan`, `is_gluten_free`
- Added `allergens` field (comma-separated) to Ingredient model
- Created Alembic migration `002_add_dietary_fields.py`
- Updated `IngredientCreate` and `IngredientRead` schemas with new fields
- Added `_check_dietary_compatibility()` helper in recommendation service
- Extended `/recommendations` endpoint with `vegetarian`, `vegan`, `gluten_free`, `exclude_allergens` params

### Step 6.3 - Expiration Awareness ✅
- [x] Prioritize recipes using soon-to-expire ingredients (`prioritize_expiring=true`)
- [x] Warn about expired pantry items (`GET /pantry/expiring`)

**Implementation Details:**
- Added `get_expiring_ingredient_ids()` helper function
- Extended recommendation algorithm to count expiring ingredients per recipe
- Added `uses_expiring_ingredients` field to `RecipeMatch` response
- When `prioritize_expiring=true`, recipes are sorted by expiring ingredients first

---

## Phase 7: Testing ✅

### Step 7.1 - Test Setup
- [x] Configure pytest with async support in `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  asyncio_mode = "auto"
  asyncio_default_fixture_loop_scope = "function"
  testpaths = ["tests"]
  ```
- [x] Create test database fixtures (`tests/conftest.py`)
- [x] Set up factory functions for test data (UserFactory, IngredientFactory, RecipeFactory, etc.)

### Step 7.2 - Test Coverage
- [x] Unit tests for matching algorithm (`tests/test_recommendations.py`)
- [x] Integration tests for each endpoint (all `tests/test_*.py` files)
- [x] Auth flow tests (`tests/test_auth.py`)
- [x] Edge cases (empty pantry, no matches, unauthorized access)

### Step 7.3 - Running Tests
- [x] Run all tests:
  ```bash
  uv run pytest
  ```
- [x] Run with coverage:
  ```bash
  uv run pytest --cov=app --cov-report=html
  ```

**Test Summary: 99 tests covering all endpoints and the recommendation algorithm**

---

## Phase 8: Documentation & Polish ✅

### Step 8.1 - API Documentation
- [x] Add detailed docstrings to all endpoints (with usage examples)
- [x] Include example requests/responses in OpenAPI
- [x] Add tags for grouping endpoints (Authentication, Ingredients, Pantry, Recipes, Recommendations, Favorites, Cooking History)

### Step 8.2 - README
- [x] Project overview and features
- [x] Installation instructions using uv
- [x] Environment setup guide (`.env` configuration)
- [x] API usage examples with Swagger UI at `/docs`

### Step 8.3 - Seed Data
- [x] Create seed script at `scripts/seed.py`
- [x] Populate common ingredients (~100 items across categories)
- [x] Add 25 sample recipes for demo
- [x] Run seeder:
  ```bash
  uv run python scripts/seed.py
  ```

---

## Future Enhancements (Out of Scope)

These are not part of the initial implementation but noted for potential expansion:

- 🤖 ML-based recommendations using cooking history
- 📸 Image recognition for pantry scanning
- 🛒 Integration with grocery delivery APIs
- 📊 Nutritional information per recipe
- 👥 Social features (share recipes, follow users)
- 📱 WebSocket for real-time pantry sync

---

## API Endpoint Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Get JWT token |
| GET | `/auth/me` | Current user profile |
| GET | `/ingredients` | List ingredients |
| GET | `/pantry` | User's pantry items |
| POST | `/pantry` | Add to pantry |
| PATCH | `/pantry/{id}` | Update pantry item |
| DELETE | `/pantry/{id}` | Remove from pantry |
| GET | `/recipes` | List all recipes |
| GET | `/recipes/{id}` | Recipe details |
| GET | `/recommendations` | **Matched recipes** |
| GET | `/recommendations/{id}/shopping-list` | Missing ingredients |
| GET | `/favorites` | User's favorites |
| POST | `/favorites/{recipe_id}` | Add favorite |
| DELETE | `/favorites/{recipe_id}` | Remove favorite |
| GET | `/history` | Cooking history |
| POST | `/history` | Log cooked recipe |

---

## Estimated Timeline

| Phase | Description | Est. Time |
|-------|-------------|-----------|
| 1 | Project Foundation | 1-2 hours |
| 2 | Data Models | 2-3 hours |
| 3 | Pydantic Schemas | 1-2 hours |
| 4 | Authentication | 2-3 hours |
| 5 | API Endpoints | 4-6 hours |
| 6 | Business Logic | 2-3 hours |
| 7 | Testing | 3-4 hours |
| 8 | Documentation | 1-2 hours |
| **Total** | | **16-25 hours** |

---

*Plan created: November 29, 2025*
