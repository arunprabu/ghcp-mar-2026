# Postman Testable Data — Products REST API

Base URL: `http://localhost:8000`

All product endpoints are prefixed with `/api/v1/products`.

Valid `category` values: `Electronics`, `Clothing`, `Food`, `Home`, `Sports`, `Books`, `Other`

---

## 1. Health Check

| Field  | Value     |
| ------ | --------- |
| Method | `GET`     |
| URL    | `/health` |
| Body   | _(none)_  |

**Expected response (200 OK):**

```json
{
  "status": "ok"
}
```

---

## 2. Create Products (POST `/api/v1/products`)

### 2a. Electronics — Full payload

```json
{
  "name": "Sony WH-1000XM5 Headphones",
  "category": "Electronics",
  "description": "Industry-leading noise cancelling wireless headphones with 30-hour battery life.",
  "thumbnail_url": "https://images.example.com/sony-wh1000xm5.jpg",
  "price": 349.99,
  "discount": 10.0
}
```

**Expected response (201 Created):**

```json
{
  "id": "<uuid>",
  "name": "Sony WH-1000XM5 Headphones",
  "category": "Electronics",
  "description": "Industry-leading noise cancelling wireless headphones with 30-hour battery life.",
  "thumbnail_url": "https://images.example.com/sony-wh1000xm5.jpg",
  "price": 349.99,
  "discount": 10.0,
  "created_at": "<timestamp>",
  "updated_at": "<timestamp>"
}
```

---

### 2b. Clothing — Minimal payload (no optional fields)

```json
{
  "name": "Classic White Oxford Shirt",
  "category": "Clothing",
  "price": 49.99
}
```

**Expected response (201 Created):**

```json
{
  "id": "<uuid>",
  "name": "Classic White Oxford Shirt",
  "category": "Clothing",
  "description": null,
  "thumbnail_url": null,
  "price": 49.99,
  "discount": 0.0,
  "created_at": "<timestamp>",
  "updated_at": "<timestamp>"
}
```

---

### 2c. Books — With description, no thumbnail

```json
{
  "name": "Clean Code",
  "category": "Books",
  "description": "A handbook of agile software craftsmanship by Robert C. Martin.",
  "price": 29.95,
  "discount": 5.0
}
```

**Expected response (201 Created):** `201` with product object.

---

### 2d. Food — With thumbnail

```json
{
  "name": "Organic Green Tea (100 bags)",
  "category": "Food",
  "description": "Premium Japanese organic green tea sourced from Uji, Kyoto.",
  "thumbnail_url": "https://images.example.com/green-tea.jpg",
  "price": 14.99,
  "discount": 0.0
}
```

**Expected response (201 Created):** `201` with product object.

---

### 2e. Sports — Full payload

```json
{
  "name": "Adidas Ultraboost 23 Running Shoes",
  "category": "Sports",
  "description": "High-performance running shoes with responsive BOOST midsole cushioning.",
  "thumbnail_url": "https://images.example.com/ultraboost23.jpg",
  "price": 189.99,
  "discount": 15.0
}
```

**Expected response (201 Created):** `201` with product object.

---

## 3. List Products (GET `/api/v1/products`)

### 3a. All products (no filters)

| Field  | Value              |
| ------ | ------------------ |
| Method | `GET`              |
| URL    | `/api/v1/products` |
| Body   | _(none)_           |

**Expected response (200 OK):**

```json
{
  "items": [ ... ],
  "total": 5
}
```

---

### 3b. Filter by category

| Field  | Value                             |
| ------ | --------------------------------- |
| Method | `GET`                             |
| URL    | `/api/v1/products?category=Books` |

**Expected:** Returns only `Books` products.

---

### 3c. Filter by price range

| Field  | Value                                         |
| ------ | --------------------------------------------- |
| Method | `GET`                                         |
| URL    | `/api/v1/products?min_price=20&max_price=100` |

**Expected:** Returns products with price between 20 and 100.

---

### 3d. Sort by price descending

| Field  | Value                                            |
| ------ | ------------------------------------------------ |
| Method | `GET`                                            |
| URL    | `/api/v1/products?sort_by=price&sort_order=desc` |

**Expected:** Products ordered from highest to lowest price.

---

### 3e. Combined filter + sort

| Field  | Value                                                                              |
| ------ | ---------------------------------------------------------------------------------- |
| Method | `GET`                                                                              |
| URL    | `/api/v1/products?category=Electronics&min_price=100&sort_by=price&sort_order=asc` |

**Expected:** Electronics products over $100, sorted by price ascending.

---

## 4. Get Product by ID (GET `/api/v1/products/{id}`)

> Replace `{id}` with a UUID returned from a Create request above.

| Field  | Value                     |
| ------ | ------------------------- |
| Method | `GET`                     |
| URL    | `/api/v1/products/<uuid>` |

**Expected response (200 OK):**

```json
{
  "id": "<uuid>",
  "name": "Sony WH-1000XM5 Headphones",
  "category": "Electronics",
  ...
}
```

**Not found (404):**

```
GET /api/v1/products/00000000-0000-0000-0000-000000000000
```

```json
{
  "detail": "Product with id 00000000-0000-0000-0000-000000000000 not found"
}
```

---

## 5. Update Product (PUT `/api/v1/products/{id}`)

> All fields are optional. Send only the fields you want to change.

### 5a. Partial update — price and discount only

```json
{
  "price": 299.99,
  "discount": 20.0
}
```

**Expected response (200 OK):** Updated product with new `price` and `discount`.

---

### 5b. Full update

```json
{
  "name": "Sony WH-1000XM5 Headphones (Midnight Black)",
  "category": "Electronics",
  "description": "Updated: Now available in Midnight Black. 30-hour battery, premium ANC.",
  "thumbnail_url": "https://images.example.com/sony-wh1000xm5-black.jpg",
  "price": 329.99,
  "discount": 0.0
}
```

**Expected response (200 OK):** Fully updated product object.

---

### 5c. Change category

```json
{
  "category": "Other"
}
```

**Expected response (200 OK):** Product with updated `category`.

---

### 5d. Update with invalid price (negative) — expect 400

```json
{
  "price": -10.0
}
```

**Expected response (400 Bad Request):**

```json
{
  "detail": "Price must be greater than 0"
}
```

---

### 5e. Update non-existent product — expect 404

```
PUT /api/v1/products/00000000-0000-0000-0000-000000000000
```

```json
{
  "price": 99.99
}
```

**Expected response (404 Not Found).**

---

## 6. Delete Product (DELETE `/api/v1/products/{id}`)

### 6a. Soft delete an existing product

| Field  | Value                     |
| ------ | ------------------------- |
| Method | `DELETE`                  |
| URL    | `/api/v1/products/<uuid>` |

**Expected response (200 OK):**

```json
{
  "message": "Product with id <uuid> deleted successfully"
}
```

---

### 6b. Verify product is gone after deletion

```
GET /api/v1/products/<uuid>
```

**Expected response (404 Not Found):** Soft-deleted products are excluded from all queries.

---

### 6c. Delete non-existent product — expect 404

```
DELETE /api/v1/products/00000000-0000-0000-0000-000000000000
```

**Expected response (404 Not Found):**

```json
{
  "detail": "Product with id 00000000-0000-0000-0000-000000000000 not found"
}
```

---

## 7. Validation Error Test Cases

These requests intentionally send bad data to verify your API rejects them correctly.

### 7a. Missing required fields (POST) — expect 422

```json
{
  "description": "A product with no name or price"
}
```

---

### 7b. Invalid category value — expect 422

```json
{
  "name": "Test Product",
  "category": "InvalidCategory",
  "price": 19.99
}
```

---

### 7c. Price = 0 — expect 422 (must be > 0)

```json
{
  "name": "Free Product",
  "category": "Other",
  "price": 0
}
```

---

### 7d. Discount out of range (> 100) — expect 422

```json
{
  "name": "Over-discounted Product",
  "category": "Home",
  "price": 50.0,
  "discount": 110.0
}
```

---

### 7e. Invalid thumbnail URL format — expect 422

```json
{
  "name": "Bad URL Product",
  "category": "Electronics",
  "price": 99.99,
  "thumbnail_url": "not-a-valid-url"
}
```

---

## Quick Reference — Postman Setup

| Setting      | Value                   |
| ------------ | ----------------------- |
| Base URL     | `http://localhost:8000` |
| Content-Type | `application/json`      |
| Accept       | `application/json`      |

**Recommended test order:**

1. `GET /health` — verify server is running
2. `POST /api/v1/products` × 5 — create test data (save returned `id` values as Postman variables)
3. `GET /api/v1/products` — list all, then with filters
4. `GET /api/v1/products/:id` — retrieve one by ID
5. `PUT /api/v1/products/:id` — partial and full updates
6. `DELETE /api/v1/products/:id` — soft delete one
7. Run validation error cases to confirm 422/400/404 responses
