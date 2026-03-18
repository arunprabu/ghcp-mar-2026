# Products REST API — Architecture Documentation

## Table of Contents

1. [Architectural Overview](#architectural-overview)
2. [4-Layer Architecture](#4-layer-architecture)
3. [Request Lifecycle](#request-lifecycle)
4. [Component Interactions](#component-interactions)
5. [Module Dependency Graph](#module-dependency-graph)
6. [Application Startup and Shutdown](#application-startup-and-shutdown)
7. [Database Architecture](#database-architecture)
8. [Schema Design](#schema-design)
9. [Error Flow](#error-flow)
10. [Testing Architecture](#testing-architecture)
11. [Design Decisions](#design-decisions)

---

## Architectural Overview

The Products REST API is built around a **strict 4-layer architecture** where each layer has a single, well-defined responsibility. No layer ever skips another — every request flows top-to-bottom through Routes → Services → Repositories → Models.

```
┌──────────────────────────────────────────┐
│               HTTP Client                │
└──────────────────┬───────────────────────┘
                   │ HTTP Request
                   ▼
┌──────────────────────────────────────────┐
│             Routes Layer                 │  app/routes/
│  - Parse HTTP request                    │  products.py
│  - Call service methods                  │
│  - Map domain exceptions → HTTP status   │
│  - Return HTTP response                  │
└──────────────────┬───────────────────────┘
                   │ Domain objects / exceptions
                   ▼
┌──────────────────────────────────────────┐
│            Services Layer                │  app/services/
│  - Enforce business rules                │  product_service.py
│  - Validate domain invariants            │
│  - Raise domain exceptions               │
│  - Coordinate repository calls           │
└──────────────────┬───────────────────────┘
                   │ SQLAlchemy model instances
                   ▼
┌──────────────────────────────────────────┐
│          Repositories Layer              │  app/repositories/
│  - Construct and execute SQL queries     │  product_repository.py
│  - Always filter soft-deleted records    │
│  - Return model instances or None        │
│  - No business logic                     │
└──────────────────┬───────────────────────┘
                   │ SQLAlchemy ORM
                   ▼
┌──────────────────────────────────────────┐
│             Models Layer                 │  app/models/
│  - SQLAlchemy ORM table definitions      │  product.py
│  - Column types, constraints, indexes    │
└──────────────────┬───────────────────────┘
                   │ SQL
                   ▼
┌──────────────────────────────────────────┐
│             PostgreSQL Database          │
└──────────────────────────────────────────┘
```

---

## 4-Layer Architecture

### Layer 1 — Routes (`app/routes/`)

**File:** `app/routes/products.py`

The routes layer is the **HTTP boundary** of the application. It is the only layer that knows about HTTP concepts: status codes, headers, Pydantic request/response schemas, and FastAPI's dependency injection.

**Responsibilities:**

- Declare all FastAPI route handlers (`@router.post`, `@router.get`, etc.).
- Accept and validate incoming HTTP request bodies via Pydantic schemas (`ProductCreateRequest`, `ProductUpdateRequest`).
- Inject the database session using `Depends(get_session)`.
- Instantiate `ProductService` and delegate all logic to it.
- Catch domain exceptions and translate them to `HTTPException` with the correct HTTP status code.
- Serialize the returned ORM model to a Pydantic response schema (`ProductResponse.model_validate()`).

**What it must NOT do:**

- Contain any business logic or data validation beyond Pydantic schema enforcement.
- Call `ProductRepository` directly.
- Raise domain exceptions.

---

### Layer 2 — Services (`app/services/`)

**File:** `app/services/product_service.py`

The services layer is the **business logic core** of the application. It is pure Python — it knows nothing about HTTP.

**Responsibilities:**

- Receive plain Python arguments from routes.
- Enforce business rules (e.g., price must be > 0, discount must be 0–100).
- Generate UUIDs for new records (`uuid4()`).
- Instantiate `ProductRepository` with the injected `AsyncSession`.
- Call repository methods and assemble the result.
- Raise domain-specific exceptions from `app/utils/exceptions.py` when rules are violated.
- Call `repository.commit()` after successful write operations.

**What it must NOT do:**

- Raise `HTTPException` or any HTTP-specific error.
- Construct SQL queries directly.
- Know about Pydantic schemas.

---

### Layer 3 — Repositories (`app/repositories/`)

**File:** `app/repositories/product_repository.py`

The repositories layer is the **data access layer**. It owns all SQLAlchemy query logic.

**Responsibilities:**

- Accept a `session: AsyncSession` in `__init__`.
- Implement `create`, `get_by_id`, `list_all`, `update`, `soft_delete`, `commit`, and `rollback` methods.
- Always filter `is_deleted == False` on every read query (except when explicitly required otherwise).
- Return `None` for not-found cases — never raise exceptions from this layer.
- Use `session.flush()` after writes and `session.refresh()` to reload the ORM state.

**What it must NOT do:**

- Contain any business rules (e.g., do not validate price here).
- Raise domain exceptions.
- Call `session.commit()` — commit is the service layer's responsibility.

---

### Layer 4 — Models (`app/models/`)

**File:** `app/models/product.py`

The models layer defines the **SQLAlchemy ORM table structure** that maps Python classes to database tables.

**Responsibilities:**

- Define the `Product` class that inherits from `Base`.
- Declare all columns using SQLAlchemy 2.0 `Mapped` / `mapped_column` syntax.
- Define table-level constraints, server defaults, and indexes via `__table_args__`.
- Provide a `__repr__` for debugging.

**What it must NOT do:**

- Contain business logic.
- Know about Pydantic schemas or HTTP requests.

---

## Request Lifecycle

The following traces a `POST /api/v1/products` request end-to-end:

```
1. HTTP POST /api/v1/products  (JSON body arrives)
        │
        ▼
2. FastAPI matches route → create_product() in products.py
        │
        ▼
3. Pydantic deserializes JSON → ProductCreateRequest
   - Validates field types, lengths, range constraints
   - Calls field_validator("thumbnail_url") → is_valid_url()
   - 422 returned immediately if validation fails
        │
        ▼
4. FastAPI injects AsyncSession via Depends(get_session)
        │
        ▼
5. ProductService(session) is instantiated
        │
        ▼
6. service.create_product(...) is called
   - Validates price > 0  → raise InvalidPriceError if not
   - Validates discount 0–100 → raise InvalidDiscountError if not
   - Generates UUID via uuid4()
   - Creates Product(...) ORM instance
        │
        ▼
7. repository.create(product) is called
   - session.add(product)
   - await session.flush()   ← writes to DB within transaction
   - await session.refresh(product)  ← reloads generated fields
   - Returns Product instance
        │
        ▼
8. repository.commit() is called
   - await session.commit()  ← transaction committed to PostgreSQL
        │
        ▼
9. Service returns Product ORM instance to route
        │
        ▼
10. Route calls ProductResponse.model_validate(product)
    - Converts ORM model → Pydantic schema
        │
        ▼
11. FastAPI serializes ProductResponse → JSON
    HTTP 201 Created returned to client
```

---

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          app/main.py                                        │
│  create_app()                                                               │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │  FastAPI app                                                        │     │
│  │  ├── CORSMiddleware                                                 │     │
│  │  ├── GET /health                                                    │     │
│  │  └── APIRouter  ←── app/routes/products.py (prefix: /api/v1/products) │  │
│  └────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                │ imports
                ▼
┌───────────────────────────────────────────────────┐
│              app/routes/products.py               │
│  depends on:                                      │
│  ├── app/database.py          (get_session)       │
│  ├── app/schemas/product.py   (request/response)  │
│  ├── app/services/product_service.py              │
│  └── app/utils/exceptions.py  (catch exceptions)  │
└───────────────────────────────────────────────────┘
                │ instantiates
                ▼
┌───────────────────────────────────────────────────┐
│           app/services/product_service.py          │
│  depends on:                                      │
│  ├── app/repositories/product_repository.py       │
│  ├── app/models/product.py    (Product ORM class) │
│  ├── app/constants.py         (ProductCategory)   │
│  └── app/utils/exceptions.py  (raise exceptions)  │
└───────────────────────────────────────────────────┘
                │ instantiates
                ▼
┌───────────────────────────────────────────────────┐
│        app/repositories/product_repository.py      │
│  depends on:                                      │
│  └── app/models/product.py    (Product ORM class) │
└───────────────────────────────────────────────────┘
                │ queries via SQLAlchemy AsyncSession
                ▼
┌───────────────────────────────────────────────────┐
│              app/models/product.py                │
│  depends on:                                      │
│  └── app/database.py          (Base)              │
└───────────────────────────────────────────────────┘
                │ maps to
                ▼
┌───────────────────────────────────────────────────┐
│               PostgreSQL: products table           │
└───────────────────────────────────────────────────┘
```

### Supporting Components

```
app/config.py
  └── Reads .env → exposes `settings` singleton
  └── Used by app/database.py (DATABASE_URL, pool settings)

app/constants.py
  └── ProductCategory enum  → used by routes, services, schemas, models
  └── API_V1_PREFIX         → used by routes
  └── Validation limits     → used by schemas

app/database.py
  └── Creates async SQLAlchemy engine from settings.DATABASE_URL
  └── Creates async_session factory
  └── Provides Base (used by models)
  └── Provides get_session() (used by routes via Depends)
  └── Provides init_db() / close_db() (used by app lifespan)

app/utils/__init__.py
  └── is_valid_url() regex validator → used by schemas

app/utils/exceptions.py
  └── Domain exception classes → raised by services, caught by routes

app/schemas/base.py
  └── BaseProductSchema   → extended by ProductCreateRequest, ProductResponse
  └── TimestampedMixin    → mixed into ProductResponse
```

---

## Module Dependency Graph

```
app.main
  ├── app.constants        (API_TITLE, API_VERSION, API_DESCRIPTION)
  ├── app.database         (init_db, close_db)
  └── app.routes.products  (router)

app.routes.products
  ├── app.constants        (ProductCategory, API_V1_PREFIX)
  ├── app.database         (get_session)
  ├── app.schemas.product  (request/response schemas)
  ├── app.services.product_service
  └── app.utils.exceptions

app.services.product_service
  ├── app.constants        (ProductCategory)
  ├── app.models.product   (Product)
  ├── app.repositories.product_repository
  └── app.utils.exceptions

app.repositories.product_repository
  └── app.models.product   (Product)

app.models.product
  └── app.database         (Base)

app.schemas.product
  ├── app.constants        (ProductCategory)
  ├── app.schemas.base     (BaseProductSchema, TimestampedMixin)
  └── app.utils            (is_valid_url)

app.database
  └── app.config           (settings)

app.config
  └── pydantic_settings    (BaseSettings, reads .env)
```

---

## Application Startup and Shutdown

FastAPI's `lifespan` context manager in `app/main.py` handles startup and shutdown:

```
Application Start
      │
      ▼
lifespan(app) enters
      │
      ▼
await init_db()
  └── engine.begin() → Base.metadata.create_all()
      (Creates tables if they don't exist — useful for dev without Alembic)
      │
      ▼
(Application serves requests)
      │
      ▼
lifespan(app) exits (on shutdown signal)
      │
      ▼
await close_db()
  └── engine.dispose()
      (Closes all pooled connections gracefully)
```

Errors during `init_db()` or `close_db()` are caught and logged as warnings to prevent crashes during startup if the database is temporarily unavailable.

---

## Database Architecture

### Async Engine Configuration

```
create_async_engine(
    DATABASE_URL,          ← from settings / .env
    echo=DEBUG,            ← logs all SQL when DEBUG=True
    pool_size=20,          ← persistent connections
    max_overflow=10,       ← burst capacity
    pool_recycle=3600,     ← recycle connections after 1 hour
    pool_pre_ping=True,    ← test connection health before use
)
```

### Session Lifecycle

```
get_session() (generator — used with FastAPI Depends)
    │
    ├── async with async_session() as session:
    │       yield session          ← provided to route handler
    │                              ← session auto-closed after request
    │
    └── (no explicit commit/rollback here — delegated to service)
```

The session is configured with:

- `expire_on_commit=False` — ORM objects remain accessible after commit (important for async patterns).
- `autocommit=False` — explicit commits required.
- `autoflush=False` — flushes are explicit in the repository layer.

### Soft Deletion Pattern

All read queries in `ProductRepository` include the filter `Product.is_deleted == False`. Deleted records remain in the database with `is_deleted = true` and are invisible to all standard queries. This pattern:

- Preserves a full audit trail of all records ever created.
- Allows data recovery without needing database backups.
- Avoids cascading deletes in relational integrity scenarios.

---

## Schema Design

### Inheritance Hierarchy

```
pydantic.BaseModel
    │
    ├── BaseProductSchema               (app/schemas/base.py)
    │   ├── name, category, description,
    │   │   thumbnail_url, price, discount
    │   │
    │   ├── ProductCreateRequest        (app/schemas/product.py)
    │   │   └── category: ProductCategory (enum, strict)
    │   │   └── @field_validator thumbnail_url
    │   │
    │   └── ProductResponse             (app/schemas/product.py)
    │       ├── id: str
    │       └── (mixes in TimestampedMixin)
    │
    ├── TimestampedMixin                (app/schemas/base.py)
    │   └── created_at, updated_at
    │
    ├── ProductUpdateRequest            (app/schemas/product.py)
    │   └── All fields optional
    │   └── @field_validator thumbnail_url
    │
    ├── ProductListResponse             (app/schemas/product.py)
    │   └── items: list[ProductResponse]
    │   └── total: int
    │
    └── ProductDeleteResponse           (app/schemas/product.py)
        └── message: str
```

### ORM → Schema Conversion

All response schemas use `model_validate()` with `from_attributes=True` (Pydantic v2 ORM mode):

```python
ProductResponse.model_validate(product)   # product is a SQLAlchemy ORM instance
```

This eliminates manual field mapping between the ORM model and the API response.

---

## Error Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                          Pydantic Schemas                        │
│  Invalid input → ValidationError → FastAPI → 422 Unprocessable   │
│  (No code needed in routes — FastAPI handles automatically)       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                         Service Layer                            │
│                                                                  │
│  price <= 0          → raise InvalidPriceError(msg)              │
│  discount not 0-100  → raise InvalidDiscountError(msg)           │
│  product not found   → raise ProductNotFoundError(msg)           │
└───────────────────────────┬──────────────────────────────────────┘
                            │ propagates up
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                          Routes Layer                            │
│                                                                  │
│  except ProductNotFoundError   → HTTPException(404)              │
│  except InvalidPriceError      → HTTPException(400)              │
│  except InvalidDiscountError   → HTTPException(400)              │
└──────────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    HTTP Response to Client
                    { "detail": "human readable message" }
```

Internal tracebacks and system-level errors are never surfaced to the caller.

---

## Testing Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    pytest test runner                     │
└────────────────────────────┬─────────────────────────────┘
                             │ runs
                             ▼
┌──────────────────────────────────────────────────────────┐
│                  tests/conftest.py                        │
│                                                           │
│  event_loop (session scope)                               │
│  ├── Creates single asyncio event loop for the session    │
│                                                           │
│  test_db (function scope)                                 │
│  ├── Creates sqlite+aiosqlite:///:memory: engine          │
│  ├── Runs Base.metadata.create_all()                     │
│  ├── Yields a fresh AsyncSession                          │
│  └── Disposes engine after each test                      │
│                                                           │
│  client (function scope, depends on test_db)              │
│  ├── Overrides get_session dependency with test_db        │
│  ├── Creates httpx.AsyncClient(app=app, base_url=...)     │
│  └── Clears dependency_overrides after each test          │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────┐
│              tests/test_products.py                       │
│  TestProductAPI class                                     │
│  └── All tests receive injected AsyncClient              │
│      Every test gets a completely fresh empty database    │
└──────────────────────────────────────────────────────────┘
```

### Key Testing Design Decisions

| Decision                               | Rationale                                                                                                                  |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| In-memory SQLite instead of PostgreSQL | No external dependency; tests run anywhere; fast setup/teardown                                                            |
| Function-scoped `test_db` fixture      | Every test is fully isolated — no shared state between tests                                                               |
| `app.dependency_overrides`             | Swaps the real DB session without modifying application code                                                               |
| `httpx.AsyncClient`                    | Sends real HTTP requests through the full ASGI stack (routes → services → repositories) — these are true integration tests |
| `asyncio_mode = auto` in pytest.ini    | Removes the need for `@pytest.mark.asyncio` on every test method                                                           |

---

## Design Decisions

### Why 4-layer Architecture?

| Alternative             | Problem                                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------ |
| Fat routes              | Business logic in routes is hard to test without HTTP                                            |
| No repository layer     | Business logic directly talking to SQLAlchemy is hard to mock and leads to duplicated query code |
| 2-layer (route + model) | Does not scale; mixing DB, business, and HTTP concerns in one file                               |

The 4-layer approach allows each layer to be tested, replaced, or evolved independently.

---

### Why Soft Delete?

Hard deletes destroy data permanently. Soft deletion (`is_deleted = true`) means:

- Deleted products are permanently hidden from the API without data loss.
- Data can be recovered without a backup restore.
- Referential integrity is preserved if other tables reference products in the future.
- The `idx_product_is_deleted` index ensures that filtering deleted records does not cause full table scans.

---

### Why SQLAlchemy Async (2.0 style)?

| Feature                    | Benefit                                                                       |
| -------------------------- | ----------------------------------------------------------------------------- |
| `AsyncSession`             | Non-blocking I/O — the ASGI event loop is never blocked by DB calls           |
| `Mapped` / `mapped_column` | Type-safe ORM declarations; compatible with mypy                              |
| `expire_on_commit=False`   | ORM objects remain usable after `await session.commit()` in async context     |
| `pool_pre_ping=True`       | Automatically detects and replaces broken connections without manual handling |

---

### Why Pydantic v2?

- **Speed** — Pydantic v2 is 5–50x faster than v1 at validation.
- **`model_validate()`** — Clean ORM-to-schema conversion with `from_attributes=True`.
- **`field_validator`** — Per-field custom validation (URL format) without polluting model logic.
- **`Field(...)` descriptors** — Self-documenting fields that power the Swagger UI automatically.

---

### Why UUID for IDs?

- UUIDs are globally unique — prevents ID enumeration attacks (predictable integer IDs expose record counts and allow IDOR attacks).
- IDs can be generated in the application layer (`uuid4()`) before any database round-trip, enabling optimistic inserts.
- Stored as a string in PostgreSQL `UUID` type — safe across both PostgreSQL (production) and SQLite (testing).

---

### Why uv as the Package Manager?

- **Speed** — uv installs packages significantly faster than pip.
- **`pyproject.toml`-native** — manages dependencies, dev-dependencies, and build metadata in a single file.
- **Lock file support** — reproducible builds across environments.
- **`uv run`** — runs commands inside the managed virtual environment without activation.
