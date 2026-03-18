# GitHub Copilot Instructions — Products REST API

## General Rules

- Never access the `.env` file. Use `.env.example` as the reference for environment variables.
- Always use `async/await` for all database operations and route handlers.
- All code must include type hints.

---

## Project Overview

A production-ready REST API for managing products, built with **FastAPI** and **PostgreSQL**.

| Component       | Technology              |
| --------------- | ----------------------- |
| Language        | Python 3.12+            |
| Web Framework   | FastAPI                 |
| ASGI Server     | Uvicorn                 |
| ORM             | SQLAlchemy 2.0 (async)  |
| Database        | PostgreSQL              |
| Validation      | Pydantic v2             |
| Migrations      | Alembic                 |
| Testing         | Pytest + pytest-asyncio |
| Package Manager | uv                      |
| Linting         | Ruff                    |
| Formatting      | Black (line length 100) |
| Type Checking   | mypy                    |

---

## Architecture

The application follows a strict **4-layer architecture**. Every request flows top-to-bottom through these layers:

```
HTTP Request
     │
     ▼
┌─────────────┐
│   Routes    │  app/routes/        — FastAPI routers, request/response handling, HTTP status codes
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Services   │  app/services/      — Business logic, validation rules, domain exceptions
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  Repositories    │  app/repositories/  — Data access layer, SQLAlchemy queries only
└──────┬───────────┘
       │
       ▼
┌─────────────┐
│   Models    │  app/models/        — SQLAlchemy ORM models (mapped to DB tables)
└─────────────┘
```

### Supporting Layers

| Directory          | Purpose                                             |
| ------------------ | --------------------------------------------------- |
| `app/schemas/`     | Pydantic request/response schemas (no DB logic)     |
| `app/config.py`    | App settings via `pydantic-settings` (reads `.env`) |
| `app/constants.py` | Enums, API prefix, and validation constants         |
| `app/database.py`  | SQLAlchemy async engine, session factory, `Base`    |
| `app/utils/`       | Shared utilities and custom domain exceptions       |
| `migrations/`      | Alembic migration scripts                           |
| `tests/`           | Integration tests using in-memory SQLite            |

### API Structure

All endpoints are prefixed with `/api/v1`.

| Method   | Endpoint                | Description                |
| -------- | ----------------------- | -------------------------- |
| `GET`    | `/health`               | Health check               |
| `POST`   | `/api/v1/products`      | Create a product           |
| `GET`    | `/api/v1/products`      | List products (filterable) |
| `GET`    | `/api/v1/products/{id}` | Get product by ID          |
| `PUT`    | `/api/v1/products/{id}` | Full/partial update        |
| `DELETE` | `/api/v1/products/{id}` | Soft delete                |

---

## Naming Conventions

### Files and Directories

- All file and directory names use `snake_case`.
- Route files are named after the resource (e.g., `products.py`).
- One resource per file across all layers.

### Python

- **Classes**: `PascalCase` — e.g., `ProductService`, `ProductCreateRequest`
- **Functions / methods**: `snake_case` — e.g., `create_product`, `get_by_id`
- **Variables**: `snake_case` — e.g., `product_id`, `sort_order`
- **Constants / Enums**: `UPPER_SNAKE_CASE` for module-level constants (e.g., `API_V1_PREFIX`); `PascalCase` for `Enum` classes (e.g., `ProductCategory`)
- **Private methods**: prefix with `_` — e.g., `_build_filters`

### Database

- Table names: `snake_case`, plural — e.g., `products`
- Column names: `snake_case` — e.g., `is_deleted`, `thumbnail_url`, `created_at`
- Index names: `idx_{table}_{column}` — e.g., `idx_product_category`

### Schemas

- Request schemas: `{Resource}CreateRequest`, `{Resource}UpdateRequest`
- Response schemas: `{Resource}Response`, `{Resource}ListResponse`

### Exceptions

- Custom exceptions: `{Resource}{Issue}Error` — e.g., `ProductNotFoundError`, `InvalidPriceError`

---

## Coding Conventions

### General

- Every Python file starts with a module-level docstring.
- All public methods and classes must have docstrings.
- Maximum line length is **100 characters**.
- Imports are grouped: stdlib → third-party → local, separated by blank lines.

### Routes (`app/routes/`)

- Routes only handle HTTP concerns: parsing requests, calling services, returning responses.
- No business logic or direct DB calls in routes.
- Catch domain exceptions and map them to appropriate HTTP status codes.
- Use `Depends(get_session)` for database session injection.

### Services (`app/services/`)

- All business logic lives exclusively in the service layer.
- Services receive a `session: AsyncSession` and instantiate the repository internally.
- Raise domain-specific exceptions (from `app/utils/exceptions.py`), never HTTP exceptions.

### Repositories (`app/repositories/`)

- Only contain SQLAlchemy query logic — no business rules.
- Always filter out soft-deleted records (`is_deleted == False`) unless explicitly required.
- Return `None` for not-found cases; never raise exceptions from repositories.

### Models (`app/models/`)

- SQLAlchemy ORM models use `Mapped` and `mapped_column` (SQLAlchemy 2.0 style).
- All models inherit from `Base` (defined in `app/database.py`).
- `id` is a UUID stored as a string (PostgreSQL `UUID` type).
- Always include `created_at` and `updated_at` with `server_default=func.now()`.
- Soft deletes are implemented via `is_deleted: bool` — never hard delete records.

### Schemas (`app/schemas/`)

- All schemas inherit from `BaseModel` (Pydantic v2).
- Request schemas use `Field(...)` with descriptions for every field.
- Use `field_validator` for custom validations (e.g., URL format).
- Response schemas use `model_validate()` for ORM-to-schema conversion.

### Configuration

- All settings come from `app/config.py` via the `settings` singleton.
- Secrets and environment-specific values must be defined in `.env` (local, never committed).
- Use `.env.example` as the canonical reference for required environment variables.

### Error Handling

- Define all domain exceptions in `app/utils/exceptions.py`.
- Services raise domain exceptions; routes translate them to `HTTPException`.
- Never expose internal error details in API responses.

---

## Development Workflow

### For Every Feature or Bug Fix

1. **Write tests first** (or alongside the implementation):
   - Add test cases in `tests/test_products.py` (or a new file per resource).
   - Tests use `pytest-asyncio` with an in-memory SQLite database.
   - Cover happy paths, edge cases, and invalid inputs.
   - Run tests with: `uv run pytest`

2. **Code Review**:
   - All code changes must go through a pull request and receive at least one peer review before merging.
   - Reviewers must verify adherence to the 4-layer architecture, naming conventions, and coding standards defined here.

3. **Security Scan**:
   - Before merging, all code must be scanned for security vulnerabilities.
   - Check against OWASP Top 10: injection attacks, broken access control, insecure configurations, exposed secrets, and dependency vulnerabilities.
   - Validate all user inputs at the schema layer (Pydantic) and enforce business rules in the service layer.
   - Never log or expose sensitive data (credentials, internal stack traces) in API responses.
   - Ensure no secrets are committed — reference `.env.example` only.

### Running the Project

```bash
# Install dependencies
uv sync

# Run the API server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Format
uv run black .
```

### Database Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one step
uv run alembic downgrade -1
```

To know more about this project, please refer docs/project.md
