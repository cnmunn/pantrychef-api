# 🍳 PantryChef API

A FastAPI-powered recipe recommendation service that suggests meals based on ingredients you have at home.

## Features

- **Smart Recipe Matching**: Get recipe recommendations ranked by how well they match your pantry ingredients
- **Pantry Management**: Track ingredients you have at home with quantities and expiration dates
- **Favorites & History**: Save favorite recipes and track what you've cooked
- **Dietary Filtering**: Filter recipes by dietary restrictions (vegetarian, vegan, gluten-free)

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with async SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Auth**: JWT with python-jose
- **Package Manager**: uv

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and navigate to project
cd stl-test

# Install dependencies
uv sync

# Copy environment template and configure
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
uv run alembic upgrade head

# Start the development server
uv run uvicorn app.main:app --reload
```

### Environment Variables

Create a `.env` file based on `.env.example`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/pantrychef` |
| `SECRET_KEY` | JWT signing key | (change in production!) |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | `30` |
| `DEBUG` | Enable debug mode | `false` |

## Development

```bash
# Run development server with auto-reload
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=app --cov-report=html

# Lint code
uv run ruff check .

# Format code
uv run ruff format .

# Run database migrations
uv run alembic upgrade head
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
stl-test/
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
├── alembic/                 # Database migrations
├── scripts/                 # Utility scripts
├── tests/                   # Test suite
├── .env.example             # Environment template
└── pyproject.toml           # Project configuration
```

## License

MIT
