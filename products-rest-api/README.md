# Products REST API

A professional FastAPI-based REST API for managing products with PostgreSQL database backend.

## 🚀 Features

- ✅ **Create** products with validation
- ✅ **Read** products with filtering and sorting
- ✅ **Update** products (full and partial updates)
- ✅ **Delete** products (soft delete)
- ✅ **Filter** by category, price range
- ✅ **Sort** by name, price, and created_at
- ✅ **Async/Await** throughout for high performance
- ✅ **Type hints** for better code quality
- ✅ **Comprehensive testing** with pytest
- ✅ **Database migrations** with Alembic
- ✅ **Professional project structure**

## 📋 Tech Stack

| Component           | Technology | Version |
| ------------------- | ---------- | ------- |
| **Language**        | Python     | 3.12+   |
| **Web Framework**   | FastAPI    | Latest  |
| **ASGI Server**     | Uvicorn    | Latest  |
| **ORM**             | SQLAlchemy | 2.0+    |
| **Database**        | PostgreSQL | Latest  |
| **Validation**      | Pydantic   | v2      |
| **Migrations**      | Alembic    | Latest  |
| **Testing**         | Pytest     | Latest  |
| **Package Manager** | uv         | Latest  |

## 📦 Data Model

### Product Fields

- **id** (UUID): Unique identifier
- **name** (string, max 255): Product name
- **category** (enum): Product category (Electronics, Clothing, Food, Home, Sports, Books, Other)
- **description** (string, optional): Product description
- **thumbnail_url** (string, optional): URL to product image
- **price** (decimal): Product price (must be > 0)
- **discount** (decimal): Discount percentage (0-100, default: 0)
- **is_deleted** (boolean): Soft delete flag
- **created_at** (timestamp): Auto-managed creation timestamp
- **updated_at** (timestamp): Auto-managed update timestamp

## 🏗️ Project Structure

```
products-rest-api/
├── app/
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic layer
│   ├── routes/              # API endpoints
│   ├── utils/               # Utilities and exceptions
│   ├── config.py            # Configuration management
│   ├── constants.py         # Application constants
│   ├── database.py          # Database setup
│   └── main.py              # FastAPI application
├── tests/                   # Test suite
├── migrations/              # Alembic database migrations
├── pyproject.toml           # Project dependencies (uv)
├── pytest.ini               # Pytest configuration
├── .env                     # Environment variables
├── .env.example             # Environment template
└── README.md                # This file
```

## 🔌 API Endpoints

All endpoints are prefixed with `/api/v1`

### Products

| Method   | Endpoint         | Description                  |
| -------- | ---------------- | ---------------------------- |
| `POST`   | `/products`      | Create product               |
| `GET`    | `/products`      | List products (with filters) |
| `GET`    | `/products/{id}` | Get product by ID            |
| `PUT`    | `/products/{id}` | Update product               |
| `DELETE` | `/products/{id}` | Soft delete product          |

### Health

| Method | Endpoint  | Description  |
| ------ | --------- | ------------ |
| `GET`  | `/health` | Health check |

## 📝 API Examples

### Create Product

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

### List Products with Filters

```bash
# List all products
curl http://localhost:8000/api/v1/products

# Filter by category
curl http://localhost:8000/api/v1/products?category=Electronics

# Filter by price range
curl http://localhost:8000/api/v1/products?min_price=100&max_price=1000

# Sort by price descending
curl http://localhost:8000/api/v1/products?sort_by=price&sort_order=desc

# Combine filters
curl "http://localhost:8000/api/v1/products?category=Electronics&min_price=500&sort_by=price&sort_order=desc"
```

### Get Product

```bash
curl http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000
```

### Update Product

```bash
curl -X PUT http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MacBook Pro 2024",
    "price": 1399.99,
    "discount": 15
  }'
```

### Delete Product

```bash
curl -X DELETE http://localhost:8000/api/v1/products/550e8400-e29b-41d4-a716-446655440000
```

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.12 or higher
- PostgreSQL 12 or higher
- uv package manager

### Installation

1. **Clone/Navigate to the project directory**

```bash
cd products-rest-api
```

2. **Install uv (if not installed)**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Create virtual environment and install dependencies**

```bash
uv sync
```

4. **Copy environment template**

```bash
cp .env.example .env
```

5. **Configure environment variables**
   Edit `.env` with your PostgreSQL connection details:

```ini
DATABASE_URL=postgresql://user:password@localhost:5432/products_db
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True
```

### Database Setup

1. **Create PostgreSQL database**

```bash
# Using psql
createdb products_db
createuser products_user
```

2. **Run Alembic migrations**

```bash
# Apply migrations
alembic upgrade head

# Create new migration (if needed)
alembic revision --autogenerate -m "description"
```

## 🚀 Running the Application

### Development Server

```bash
# Using uvicorn directly
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using main.py
uv run python main.py
```

The API will be available at: `http://localhost:8000`

**Interactive API Documentation:**

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Testing

### Run All Tests

```bash
uv run pytest
```

### Run Tests with Coverage

```bash
uv run pytest --cov=app --cov-report=html
```

### Run Specific Test

```bash
uv run pytest tests/test_products.py::TestProductAPI::test_create_product -v
```

### Run Tests in Watch Mode

```bash
uv run pytest-watch
```

## 📊 Code Quality

### Format Code

```bash
uv run black app tests
```

### Lint Code

```bash
uv run ruff check app tests
```

### Type Checking

```bash
uv run mypy app
```

## 🔍 Query Parameters Guide

### List Products Query Parameters

| Parameter    | Type   | Description                               | Example       |
| ------------ | ------ | ----------------------------------------- | ------------- |
| `category`   | string | Filter by category                        | `Electronics` |
| `min_price`  | float  | Minimum price filter                      | `100.00`      |
| `max_price`  | float  | Maximum price filter                      | `500.00`      |
| `sort_by`    | string | Sort field: `name`, `price`, `created_at` | `price`       |
| `sort_order` | string | Sort direction: `asc`, `desc`             | `desc`        |

### Valid Categories

- `Electronics`
- `Clothing`
- `Food`
- `Home`
- `Sports`
- `Books`
- `Other`

## 🔐 HTTP Status Codes

| Code  | Meaning                        |
| ----- | ------------------------------ |
| `200` | Success                        |
| `201` | Created                        |
| `204` | No Content (Deleted)           |
| `400` | Bad Request (Validation error) |
| `404` | Not Found                      |
| `500` | Internal Server Error          |

## 📚 Error Handling

All errors return structured JSON responses:

```json
{
  "detail": "Product with ID xxx not found"
}
```

## 🛠️ Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql postgresql://user:password@localhost:5432/products_db

# Check .env file configuration
cat .env
```

### Port Already in Use

```bash
# Run on different port
uv run python main.py --port 8001
# Or set SERVER_PORT=8001 in .env
```

### Import Errors

```bash
# Reinstall dependencies
uv sync --reinstall
```

## 📖 Development Guidelines

### Adding a New Field

1. Update `Product` model in `app/models/product.py`
2. Create Alembic migration: `alembic revision --autogenerate -m "add_field"`
3. Update schemas in `app/schemas/product.py`
4. Update service logic in `app/services/product_service.py`
5. Add tests in `tests/test_products.py`

### Adding a New Endpoint

1. Add method in `app/services/product_service.py`
2. Add route in `app/routes/products.py`
3. Add test in `tests/test_products.py`

## 🤝 Contributing

1. Create a feature branch
2. Follow the existing code style
3. Add tests for new features
4. Run `black`, `ruff`, and `mypy` before committing
5. Ensure all tests pass: `pytest`

## 📄 License

MIT

## 📞 Support

For issues, questions, or suggestions, please open an issue in the repository.

---

**Built with ❤️ using FastAPI and PostgreSQL**
