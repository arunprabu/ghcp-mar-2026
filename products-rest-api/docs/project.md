# Products REST API — Project Documentation

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Data Model](#data-model)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)
7. [Database Migrations](#database-migrations)
8. [Testing](#testing)
9. [Development Workflow](#development-workflow)
10. [Running the Application](#running-the-application)
11. [Error Handling](#error-handling)
12. [Naming Conventions](#naming-conventions)
13. [Security Considerations](#security-considerations)

---

## Overview

Products REST API is a production-ready, asynchronous REST API built with **FastAPI** and **PostgreSQL**. It provides full CRUD operations for managing a product catalogue, including filtering, sorting, and soft deletion. The API is designed around a clean 4-layer architecture that strictly separates HTTP handling, business logic, data access, and the database model.

**API base path:** `/api/v1`

**API version:** `1.0.0`

---

## Tech Stack

| Component        | Technology              | Version                      |
| ---------------- | ----------------------- | ---------------------------- |
| Language         | Python                  | 3.12+                        |
| Web Framework    | FastAPI                 | >= 0.100.0                   |
| ASGI Server      | Uvicorn                 | >= 0.24.0                    |
| ORM              | SQLAlchemy (async)      | >= 2.0.0                     |
| Database         | PostgreSQL              | 12+                          |
| DB Driver        | psycopg (v3)            | >= 3.1.0                     |
| Validation       | Pydantic v2             | >= 2.0.0                     |
| Settings         | pydantic-settings       | >= 2.0.0                     |
| Migrations       | Alembic                 | >= 1.13.0                    |
| Testing          | pytest + pytest-asyncio | >= 7.0.0                     |
| HTTP Test Client | httpx                   | >= 0.24.0                    |
| Package Manager  | uv                      | Latest                       |
| Linting          | Ruff                    | >= 0.1.0                     |
| Formatting       | Black                   | >= 23.0.0 (line length: 100) |
| Type Checking    | mypy                    | >= 1.0.0                     |

---

## Project Structure

```
products-rest-api/
│
├── app/                            # Application package
│   ├── __init__.py
│   ├── main.py                     # FastAPI app factory, lifespan, CORS, router registration
│   ├── config.py                   # Settings via pydantic-settings (reads .env)
│   ├── constants.py                # Enums, API prefix, validation limits
│   ├── database.py                 # Async SQLAlchemy engine, session factory, Base
│   │
│   ├── models/                     # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   └── product.py              # Product table definition
│   │
│   ├── schemas/                    # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseProductSchema, TimestampedMixin
│   │   └── product.py              # CreateRequest, UpdateRequest, Response schemas
│   │
│   ├── repositories/               # Data access layer (SQLAlchemy queries only)
│   │   ├── __init__.py
│   │   └── product_repository.py   # ProductRepository class
│   │
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   └── product_service.py      # ProductService class
│   │
│   ├── routes/                     # FastAPI routers (HTTP layer)
│   │   ├── __init__.py
│   │   └── products.py             # Product CRUD endpoints
│   │
│   └── utils/                      # Shared utilities
│       ├── __init__.py             # is_valid_url() helper
│       └── exceptions.py           # Domain exception classes
│
├── migrations/                     # Alembic database migrations
│   ├── alembic.ini
│   ├── env.py                      # Alembic environment (sync mode)
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial.py          # Initial migration: creates products table + indexes
│
├── tests/                          # Integration test suite
│   ├── __init__.py
│   ├── conftest.py                 # Fixtures: in-memory SQLite DB, AsyncClient
│   └── test_products.py            # TestProductAPI class with all test cases
│
├── docs/                           # Documentation
│   ├── project.md                  # This file
│   └── arch.md                     # Architecture documentation
│
├── pyproject.toml                  # Project metadata & dependencies (uv/pip)
├── pytest.ini                      # Pytest configuration
├── main.py                         # Top-level entry point (imports app from app.main)
├── .env.example                    # Environment variable template (reference only)
├── README.md                       # Quick-start guide
└── notes.md                        # Original requirements & project notes
```

---

## Data Model

### `products` Table

| Column          | Type              | Constraints                          | Description                            |
| --------------- | ----------------- | ------------------------------------ | -------------------------------------- |
| `id`            | UUID (string)     | Primary Key, Not Null                | Unique identifier, generated as UUIDv4 |
| `name`          | VARCHAR(255)      | Not Null                             | Product name                           |
| `category`      | VARCHAR(50)       | Not Null                             | Product category (enum value)          |
| `description`   | TEXT              | Nullable                             | Long-form product description          |
| `thumbnail_url` | VARCHAR(500)      | Nullable                             | URL to product image                   |
| `price`         | NUMERIC(10, 2)    | Not Null                             | Product price; must be > 0             |
| `discount`      | NUMERIC(5, 2)     | Not Null, Default 0.0                | Discount percentage; range 0–100       |
| `is_deleted`    | BOOLEAN           | Not Null, Default false              | Soft-delete flag                       |
| `created_at`    | TIMESTAMP WITH TZ | Not Null, Default now()              | Record creation timestamp              |
| `updated_at`    | TIMESTAMP WITH TZ | Not Null, Default now(), auto-update | Last modification timestamp            |

### Database Indexes

| Index Name               | Column(s)    | Purpose                                     |
| ------------------------ | ------------ | ------------------------------------------- |
| `idx_product_name`       | `name`       | Fast name-based lookups and sorting         |
| `idx_product_category`   | `category`   | Fast category filter queries                |
| `idx_product_is_deleted` | `is_deleted` | Efficient soft-delete filtering (all reads) |

### Product Categories (Enum)

Defined in `app/constants.py` as `ProductCategory`:

| Value         |
| ------------- |
| `Electronics` |
| `Clothing`    |
| `Food`        |
| `Home`        |
| `Sports`      |
| `Books`       |
| `Other`       |

---

## API Reference

All product endpoints are prefixed with `/api/v1/products`. Tag: `products`.

### Health Check

#### `GET /health`

Returns the application health status.

**Response `200 OK`**

```json
{ "status": "healthy" }
```

---

### Products

#### `POST /api/v1/products` — Create a Product

**Request Body**

| Field           | Type   | Required | Constraints                | Description          |
| --------------- | ------ | -------- | -------------------------- | -------------------- |
| `name`          | string | Yes      | length 1–255               | Product name         |
| `category`      | string | Yes      | Must be a valid enum value | Product category     |
| `price`         | float  | Yes      | > 0                        | Product price        |
| `description`   | string | No       | max 5000 chars             | Product description  |
| `thumbnail_url` | string | No       | max 500 chars, valid URL   | URL to product image |
| `discount`      | float  | No       | 0.0–100.0, default 0.0     | Discount percentage  |

**Example Request**

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MacBook Pro",
    "category": "Electronics",
    "price": 1299.99,
    "description": "High-performance laptop",
    "thumbnail_url": "https://example.com/macbook.jpg",
    "discount": 10
  }'
```

**Response `201 Created`**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "MacBook Pro",
  "category": "Electronics",
  "price": 1299.99,
  "description": "High-performance laptop",
  "thumbnail_url": "https://example.com/macbook.jpg",
  "discount": 10.0,
  "created_at": "2026-03-17T10:00:00Z",
  "updated_at": "2026-03-17T10:00:00Z"
}
```

**Error Responses**

- `400 Bad Request` — Invalid price or discount value.
- `422 Unprocessable Entity` — Pydantic validation failure (missing required fields, wrong types, invalid URL format, out-of-range values).

---

#### `GET /api/v1/products` — List Products

**Query Parameters**

| Parameter    | Type   | Required | Default | Description                                  |
| ------------ | ------ | -------- | ------- | -------------------------------------------- |
| `category`   | string | No       | —       | Filter by category (must match enum value)   |
| `min_price`  | float  | No       | —       | Minimum price filter (inclusive)             |
| `max_price`  | float  | No       | —       | Maximum price filter (inclusive)             |
| `sort_by`    | string | No       | `name`  | Sort field: `name`, `price`, or `created_at` |
| `sort_order` | string | No       | `asc`   | Sort direction: `asc` or `desc`              |

**Example Requests**

```bash
# All products
curl http://localhost:8000/api/v1/products

# Filter by category
curl "http://localhost:8000/api/v1/products?category=Electronics"

# Price range
curl "http://localhost:8000/api/v1/products?min_price=100&max_price=1000"

# Sort by price descending
curl "http://localhost:8000/api/v1/products?sort_by=price&sort_order=desc"

# Combined filters
curl "http://localhost:8000/api/v1/products?category=Electronics&min_price=500&sort_by=price&sort_order=desc"
```

**Response `200 OK`**

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "MacBook Pro",
      "category": "Electronics",
      "price": 1299.99,
      "discount": 10.0,
      "description": "High-performance laptop",
      "thumbnail_url": "https://example.com/macbook.jpg",
      "created_at": "2026-03-17T10:00:00Z",
      "updated_at": "2026-03-17T10:00:00Z"
    }
  ],
  "total": 1
}
```

Soft-deleted products are always excluded from this list.

---

#### `GET /api/v1/products/{product_id}` — Get Product by ID

**Path Parameter**

| Parameter    | Type   | Description       |
| ------------ | ------ | ----------------- |
| `product_id` | string | Product UUID (v4) |

**Example Request**

```bash
curl http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000
```

**Response `200 OK`** — Same structure as a single item in the list response above.

**Error Responses**

- `404 Not Found` — Product does not exist or has been soft-deleted.

---

#### `PUT /api/v1/products/{product_id}` — Update a Product

Supports both full and partial updates — only the fields provided in the body are updated. Fields omitted from the request body are left unchanged.

**Path Parameter**

| Parameter    | Type   | Description       |
| ------------ | ------ | ----------------- |
| `product_id` | string | Product UUID (v4) |

**Request Body** — All fields are optional.

| Field           | Type   | Constraints                |
| --------------- | ------ | -------------------------- |
| `name`          | string | length 1–255               |
| `category`      | string | Must be a valid enum value |
| `price`         | float  | > 0                        |
| `description`   | string | max 5000 chars             |
| `thumbnail_url` | string | max 500 chars, valid URL   |
| `discount`      | float  | 0.0–100.0                  |

**Example Request**

```bash
curl -X PUT http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MacBook Pro 2024",
    "price": 1399.99,
    "discount": 15
  }'
```

**Response `200 OK`** — Full updated product object.

**Error Responses**

- `400 Bad Request` — Invalid price or discount.
- `404 Not Found` — Product not found or soft-deleted.
- `422 Unprocessable Entity` — Pydantic validation error.

---

#### `DELETE /api/v1/products/{product_id}` — Soft Delete a Product

Marks the product as deleted (`is_deleted = true`). The record is retained in the database and is excluded from all subsequent reads.

**Path Parameter**

| Parameter    | Type   | Description       |
| ------------ | ------ | ----------------- |
| `product_id` | string | Product UUID (v4) |

**Example Request**

```bash
curl -X DELETE http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000
```

**Response `200 OK`**

```json
{
  "message": "Product with id 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
}
```

**Error Responses**

- `404 Not Found` — Product not found or already soft-deleted.

---

## Configuration

All configuration is managed through `app/config.py` using `pydantic-settings`. Settings are loaded from environment variables or the `.env` file at startup. Never commit `.env` — use `.env.example` as the canonical reference.

### Environment Variables

| Variable          | Default                                                 | Description                         |
| ----------------- | ------------------------------------------------------- | ----------------------------------- |
| `SERVER_NAME`     | `Products API`                                          | Display name for the server         |
| `SERVER_HOST`     | `0.0.0.0`                                               | Host to bind the ASGI server        |
| `SERVER_PORT`     | `8000`                                                  | Port to bind the ASGI server        |
| `DEBUG`           | `False`                                                 | Enable SQLAlchemy echo + debug mode |
| `DATABASE_URL`    | `postgresql://user:password@localhost:5432/products_db` | PostgreSQL connection string        |
| `DB_POOL_SIZE`    | `20`                                                    | SQLAlchemy connection pool size     |
| `DB_MAX_OVERFLOW` | `10`                                                    | Max overflow connections above pool |
| `DB_POOL_RECYCLE` | `3600`                                                  | Connection recycle time (seconds)   |
| `LOG_LEVEL`       | `INFO`                                                  | Python logging level                |

### Connection Pooling

The async engine is configured with:

- **pool_size:** 20 — persistent connections kept alive.
- **max_overflow:** 10 — extra connections allowed when pool is exhausted.
- **pool_recycle:** 3600 seconds — prevents stale connections.
- **pool_pre_ping:** `True` — validates connections before use.

---

## Database Migrations

Migrations are managed with **Alembic** and stored in `migrations/versions/`.

### Available Migrations

| Revision      | Description                                   |
| ------------- | --------------------------------------------- |
| `001_initial` | Create `products` table and its three indexes |

### Migration Commands

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Rollback the last migration
uv run alembic downgrade -1

# Create a new auto-generated migration
uv run alembic revision --autogenerate -m "short description"

# View current migration state
uv run alembic current

# View migration history
uv run alembic history
```

### Migration File Location

```
migrations/
├── alembic.ini
├── env.py                  # Reads DATABASE_URL from app.config; imports Base.metadata
├── script.py.mako          # Template for new revision files
└── versions/
    └── 001_initial.py      # Creates products table, indexes; supports upgrade + downgrade
```

---

## Testing

The test suite uses **pytest** with **pytest-asyncio** and operates against an **in-memory SQLite database** — no real PostgreSQL instance is required to run tests. The SQLite database is recreated fresh for every individual test.

### Test Infrastructure

**`tests/conftest.py`** provides two fixtures:

| Fixture   | Scope    | Description                                                                                                  |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| `test_db` | function | Creates a fresh in-memory SQLite database, runs `create_all`, yields a session, then disposes of the engine. |
| `client`  | function | Overrides the FastAPI `get_session` dependency to inject `test_db`, then yields an `httpx.AsyncClient`.      |

The `app.dependency_overrides` mechanism is used to swap the real PostgreSQL session with the in-memory test session, ensuring complete isolation.

### Test Cases

All tests live in `tests/test_products.py` inside the `TestProductAPI` class.

| Test Method                             | Endpoint Tested                                    | Scenario Covered                                               |
| --------------------------------------- | -------------------------------------------------- | -------------------------------------------------------------- |
| `test_create_product`                   | `POST /api/v1/products`                            | Full product creation; verifies all fields in response         |
| `test_create_product_minimal`           | `POST /api/v1/products`                            | Minimal payload (required fields only); discount defaults to 0 |
| `test_create_product_invalid_price`     | `POST /api/v1/products`                            | Rejects negative price with 400                                |
| `test_create_product_invalid_discount`  | `POST /api/v1/products`                            | Rejects discount > 100 with 400                                |
| `test_list_products`                    | `GET /api/v1/products`                             | Lists all products; verifies total count                       |
| `test_list_products_filter_by_category` | `GET /api/v1/products?category=...`                | Category filter returns only matching records                  |
| `test_list_products_filter_by_price`    | `GET /api/v1/products?min_price=&max_price=`       | Price range filter returns only in-range products              |
| `test_list_products_sort`               | `GET /api/v1/products?sort_by=name&sort_order=asc` | Ascending sort by name                                         |
| `test_get_product`                      | `GET /api/v1/products/{id}`                        | Retrieves correct product by UUID                              |
| `test_get_product_not_found`            | `GET /api/v1/products/{id}`                        | Returns 404 for non-existent UUID                              |
| `test_update_product`                   | `PUT /api/v1/products/{id}`                        | Partial update; unchanged fields preserved                     |
| `test_update_product_not_found`         | `PUT /api/v1/products/{id}`                        | Returns 404 for non-existent UUID                              |
| `test_delete_product`                   | `DELETE /api/v1/products/{id}`                     | Soft deletes; product disappears from list                     |
| `test_delete_product_not_found`         | `DELETE /api/v1/products/{id}`                     | Returns 404 for non-existent UUID                              |
| `test_health_check`                     | `GET /health`                                      | Returns `{"status": "healthy"}`                                |

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a single test file
uv run pytest tests/test_products.py

# Run a single test method
uv run pytest tests/test_products.py::TestProductAPI::test_create_product
```

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
asyncio_mode = auto
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers

[coverage:run]
source = app
omit = */tests/*, */migrations/*
```

---

## Development Workflow

### Setup

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install all dependencies (creates virtual environment automatically)
uv sync

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# 4. Create and set up PostgreSQL database
createdb products_db

# 5. Run migrations
uv run alembic upgrade head
```

### Running the Server

```bash
# Development (with auto-reload)
uv run uvicorn app.main:app --reload

# Development on specific host/port
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production (no reload)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Once running, the interactive API docs are available at:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Code Quality

```bash
# Lint with Ruff
uv run ruff check .

# Auto-fix lint issues
uv run ruff check . --fix

# Format with Black
uv run black .

# Type check with mypy
uv run mypy app/
```

### Required Development Checklist

For every feature or bug fix:

1. **Write or update tests** alongside the implementation.
2. **Run the full test suite** — all tests must pass.
3. **Run linting and formatting** — code must be clean.
4. **Open a pull request** — at least one peer review required before merging.
5. **Security scan** — check against OWASP Top 10 before merging.

---

## Error Handling

The application uses a two-tier error handling strategy:

### Domain Exceptions (`app/utils/exceptions.py`)

Raised exclusively by the service layer. Never contain HTTP-specific details.

| Exception                    | When Raised                                      |
| ---------------------------- | ------------------------------------------------ |
| `ProductNotFoundError`       | A product ID does not exist or is soft-deleted   |
| `InvalidPriceError`          | Price is zero or negative                        |
| `InvalidDiscountError`       | Discount is outside the 0–100 range              |
| `InvalidCategoryError`       | Category does not match a valid enum value       |
| `ProductAlreadyDeletedError` | Attempt to operate on an already-deleted product |

### HTTP Translation (Routes Layer)

The routes layer catches domain exceptions and maps them to `HTTPException`:

| Domain Exception           | HTTP Status Code           |
| -------------------------- | -------------------------- |
| `ProductNotFoundError`     | `404 Not Found`            |
| `InvalidPriceError`        | `400 Bad Request`          |
| `InvalidDiscountError`     | `400 Bad Request`          |
| Pydantic `ValidationError` | `422 Unprocessable Entity` |

Internal stack traces and error details are never exposed in API responses.

---

## Naming Conventions

### Files and Directories

- All names use `snake_case`.
- Route files are named after their resource (e.g., `products.py`).
- One resource per file at every layer.

### Python Symbols

| Symbol Type       | Convention         | Example                             |
| ----------------- | ------------------ | ----------------------------------- |
| Classes           | `PascalCase`       | `ProductService`, `ProductResponse` |
| Functions/Methods | `snake_case`       | `create_product`, `get_by_id`       |
| Variables         | `snake_case`       | `product_id`, `sort_order`          |
| Module constants  | `UPPER_SNAKE_CASE` | `API_V1_PREFIX`, `MIN_PRICE`        |
| Enum classes      | `PascalCase`       | `ProductCategory`                   |
| Private methods   | `_snake_case`      | `_build_filters`                    |

### Database

| Object       | Convention             | Example                       |
| ------------ | ---------------------- | ----------------------------- |
| Table names  | `snake_case`, plural   | `products`                    |
| Column names | `snake_case`           | `is_deleted`, `thumbnail_url` |
| Index names  | `idx_{table}_{column}` | `idx_product_category`        |

### Schema Classes

| Schema Type     | Pattern                    | Example                 |
| --------------- | -------------------------- | ----------------------- |
| Create request  | `{Resource}CreateRequest`  | `ProductCreateRequest`  |
| Update request  | `{Resource}UpdateRequest`  | `ProductUpdateRequest`  |
| Single response | `{Resource}Response`       | `ProductResponse`       |
| List response   | `{Resource}ListResponse`   | `ProductListResponse`   |
| Delete response | `{Resource}DeleteResponse` | `ProductDeleteResponse` |

---

## Security Considerations

- **Input validation** is enforced at the schema layer by Pydantic v2. All fields have explicit type constraints, length limits, and range checks before they reach the service layer.
- **URL validation** for `thumbnail_url` uses a strict regex in `app/utils/__init__.py` (`is_valid_url()`), accepting only `http://` and `https://` URLs with valid hostnames or IP addresses.
- **Soft deletion** prevents data loss and maintains an audit trail — records are never hard-deleted from the database.
- **No secrets committed** — all sensitive values (database credentials, etc.) are read from environment variables via `.env` (excluded from version control). Reference `.env.example` only.
- **No internal error details** are exposed in API responses — raw exception messages from the service layer are only surfaced for user-facing domain errors (e.g., "Product not found"), never for unexpected system errors.
- **CORS** is configured with `allow_origins=["*"]` for development. This should be restricted to specific origins in production deployments.
- **SQL injection** is prevented by SQLAlchemy's parameterized queries — raw SQL strings are never constructed from user input.
- **Connection pre-ping** (`pool_pre_ping=True`) prevents the application from using stale or broken database connections.
