https://github.com/arunprabu/ghcp-mar-2026

I want fastapi based rest api for managing products.
api endpoint should be accessible over
example.com/api/v1/products

TechStack: Python v 3.12, fastapi (latest version), postgres
We need to capture the following data in db
name, category, description, thumbnailUrl, price, discount

features:

1. create product
2. list products
3. get product by id
4. update product
5. delete product (soft delete)

Always follow the right naming conventions
Always follow recommended practices
You have to suggest recommended project structure before generating any code. Upon my confirmation you can start to implement.

I might have missed some points. Get them clarified before generating any code.

===

0. different modes of ghcp [done]
1. Using GHCP in existing codebase [done]
2. Protecting files [done]
3. Creating docs for certain features [done]
4. arch diagram / flow diagram [done]
5. testable data [done]
6. copilot-instructions.md [done]
7. MCP server (github.com, jira server)
8. Skills [done]
   8.1. performance tuning [done]
   8.2. review
   8.3. security vulnerabilites

## Performance Optimizations Completed (2026-03-17)

### 1. Efficient COUNT Query (repository layer)

**Issue**: List endpoint was loading all products into memory just to count them.
**Fix**: Changed from `select(Product).where(...) → len(result.scalars().all())` to `select(func.count()).select_from(Product).where(...)`
**Impact**: Eliminates memory overhead for large result sets.

### 2. Database Indexes

**Issue**: `price` and `created_at` columns had no indexes despite being used in filters and sorting.
**Fix**: Added `Index("idx_product_price", "price")` and `Index("idx_product_created_at", "created_at")` to the Product model.
**Impact**: Drastically improves query performance for price-range filters and date-based sorting.

### 3. Pagination (limit/offset)

**Issue**: List endpoint returned all matching products; no pagination support.
**Fix**:

- Repository: Added `limit` and `offset` parameters to `list_all()`
- Service: Converts `page` and `page_size` to `offset = (page - 1) * page_size`
- Route: Added Query parameters with validation (page ≥ 1, page_size ≤ 100)
- Schema: Response now includes `page` and `page_size` metadata
  **Impact**: Enables efficient slicing of results; default 10 items/page, max 100.

### 4. Sort Field Whitelist (security & performance)

**Issue**: Code used `getattr(Product, sort_by, default)` — unsafe and could expose internal attributes.
**Fix**: Created `_SORT_FIELDS` dict mapping allowed sort names to SQLAlchemy column objects.
**Impact**: Prevents attribute injection attacks; guarantees valid indexed columns.

### 5. Database Connection (lazy initialization)

**Issue**: `app/database.py` instantiated SQLAlchemy engine at module-level import, breaking tests (PostgreSQL not available during pytest fixture setup).
**Fix**: Created `_get_engine()` function that lazily initializes engine on first use.
**Impact**: Tests can now import `Base` without a live database connection.

### 6. UUID Column Type (cross-database compatibility)

**Issue**: Product model used PostgreSQL-specific `PGUUID` type; SQLite tests couldn't create tables.
**Fix**: Changed from `sqlalchemy.dialects.postgresql.UUID` to generic `sqlalchemy.UUID(as_uuid=False)`.
**Impact**: Model now works with both PostgreSQL (production) and SQLite (testing).
