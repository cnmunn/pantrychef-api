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
- [ ] Test migration up/down (requires running PostgreSQL):
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

## Phase 5: API Endpoints

### Step 5.1 - Ingredients Router (`/ingredients`)
- [ ] `GET /` - List all ingredients (with category filter)
- [ ] `GET /{id}` - Get single ingredient
- [ ] `POST /` - Create ingredient (admin)
- [ ] `GET /categories` - List all categories

### Step 5.2 - Pantry Router (`/pantry`)
- [ ] `GET /` - List user's pantry items
- [ ] `POST /` - Add item to pantry
- [ ] `PATCH /{id}` - Update quantity/expiration
- [ ] `DELETE /{id}` - Remove from pantry
- [ ] `POST /bulk` - Add multiple items at once

### Step 5.3 - Recipes Router (`/recipes`)
- [ ] `GET /` - List recipes (pagination, filters)
- [ ] `GET /{id}` - Get recipe with full details
- [ ] `POST /` - Create recipe (admin)
- [ ] `GET /search` - Search by title/description

### Step 5.4 - Recommendations Router (`/recommendations`)
- [ ] `GET /` - **Core feature**: Get recipes ranked by pantry match
  - Query params: `min_match_percent`, `max_missing_ingredients`, `dietary_filters`
  - Returns recipes sorted by match percentage
- [ ] `GET /{recipe_id}/shopping-list` - Missing ingredients for a recipe

### Step 5.5 - Favorites Router (`/favorites`)
- [ ] `GET /` - List user's favorite recipes
- [ ] `POST /{recipe_id}` - Add to favorites
- [ ] `DELETE /{recipe_id}` - Remove from favorites

### Step 5.6 - Cooking History Router (`/history`)
- [ ] `GET /` - List cooking history
- [ ] `POST /` - Log a cooked recipe with rating
- [ ] `GET /stats` - Cooking statistics (most cooked, avg rating)

---

## Phase 6: Business Logic (Services Layer)

### Step 6.1 - Recipe Matching Algorithm
```
For each recipe:
  1. Get recipe's required ingredients (non-optional)
  2. Get user's pantry ingredients
  3. Calculate match = (matched / required) * 100
  4. Return sorted by match percentage descending
```

### Step 6.2 - Smart Filtering
- [ ] Filter by dietary restrictions (vegetarian, vegan, gluten-free)
- [ ] Filter by max prep time
- [ ] Filter by difficulty level
- [ ] Exclude recipes with allergen ingredients

### Step 6.3 - Expiration Awareness
- [ ] Prioritize recipes using soon-to-expire ingredients
- [ ] Warn about expired pantry items

---

## Phase 7: Testing

### Step 7.1 - Test Setup
- [ ] Configure pytest with async support in `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  asyncio_mode = "auto"
  testpaths = ["tests"]
  ```
- [ ] Create test database fixtures
- [ ] Set up factory functions for test data

### Step 7.2 - Test Coverage
- [ ] Unit tests for matching algorithm
- [ ] Integration tests for each endpoint
- [ ] Auth flow tests
- [ ] Edge cases (empty pantry, no matches)

### Step 7.3 - Running Tests
- [ ] Run all tests:
  ```bash
  uv run pytest
  ```
- [ ] Run with coverage:
  ```bash
  uv run pytest --cov=app --cov-report=html
  ```

---

## Phase 8: Documentation & Polish

### Step 8.1 - API Documentation
- [ ] Add detailed docstrings to all endpoints
- [ ] Include example requests/responses in OpenAPI
- [ ] Add tags for grouping endpoints

### Step 8.2 - README
- [ ] Project overview and features
- [ ] Installation instructions using uv:
  ```bash
  # Install uv (if not already installed)
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Clone and setup
  git clone <repo-url> stl-test
  cd stl-test
  uv sync
  
  # Copy environment template and configure
  cp .env.example .env
  
  # Run migrations
  uv run alembic upgrade head
  
  # Start server
  uv run dev
  ```
- [ ] Environment setup guide (`.env` configuration)
- [ ] API usage examples with curl

### Step 8.3 - Seed Data
- [ ] Create seed script at `scripts/seed.py`
- [ ] Add script command to `pyproject.toml`:
  ```toml
  [tool.uv.scripts]
  seed = "python scripts/seed.py"
  ```
- [ ] Populate common ingredients (~100 items)
- [ ] Add 20-30 sample recipes for demo
- [ ] Run seeder:
  ```bash
  uv run seed
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
