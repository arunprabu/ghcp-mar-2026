"""Product API integration tests."""

import pytest
from httpx import AsyncClient

from app.constants import ProductCategory


@pytest.mark.asyncio
class TestProductAPI:
    """Test suite for product API endpoints."""

    async def test_create_product(self, client: AsyncClient) -> None:
        """Test creating a product."""
        payload = {
            "name": "Test Product",
            "category": "Electronics",
            "price": 99.99,
            "description": "A test product",
            "thumbnail_url": "https://example.com/image.jpg",
            "discount": 10.0,
        }

        response = await client.post("/api/v1/products", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["category"] == "Electronics"
        assert data["price"] == 99.99
        assert "id" in data
        assert "created_at" in data

    async def test_create_product_minimal(self, client: AsyncClient) -> None:
        """Test creating a product with minimal data."""
        payload = {
            "name": "Minimal Product",
            "category": "Books",
            "price": 19.99,
        }

        response = await client.post("/api/v1/products", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal Product"
        assert data["discount"] == 0.0

    async def test_create_product_invalid_price(self, client: AsyncClient) -> None:
        """Test creating a product with invalid price."""
        payload = {
            "name": "Invalid Product",
            "category": "Food",
            "price": -10.0,
        }

        response = await client.post("/api/v1/products", json=payload)
        assert response.status_code == 400

    async def test_create_product_invalid_discount(self, client: AsyncClient) -> None:
        """Test creating a product with invalid discount."""
        payload = {
            "name": "Invalid Product",
            "category": "Food",
            "price": 10.0,
            "discount": 150.0,
        }

        response = await client.post("/api/v1/products", json=payload)
        assert response.status_code == 400

    async def test_list_products(self, client: AsyncClient) -> None:
        """Test listing all products."""
        # Create test products
        for i in range(3):
            payload = {
                "name": f"Product {i}",
                "category": "Electronics",
                "price": 10.0 + i,
            }
            await client.post("/api/v1/products", json=payload)

        response = await client.get("/api/v1/products")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 3

    async def test_list_products_filter_by_category(self, client: AsyncClient) -> None:
        """Test listing products filtered by category."""
        # Create products with different categories
        await client.post(
            "/api/v1/products",
            json={"name": "Electronics Item", "category": "Electronics", "price": 100.0},
        )
        await client.post(
            "/api/v1/products",
            json={"name": "Book Item", "category": "Books", "price": 20.0},
        )

        response = await client.get("/api/v1/products?category=Electronics")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category"] == "Electronics"

    async def test_list_products_filter_by_price(self, client: AsyncClient) -> None:
        """Test listing products filtered by price range."""
        # Create products with different prices
        await client.post(
            "/api/v1/products",
            json={"name": "Cheap Item", "category": "Books", "price": 5.0},
        )
        await client.post(
            "/api/v1/products",
            json={"name": "Expensive Item", "category": "Electronics", "price": 500.0},
        )

        response = await client.get("/api/v1/products?min_price=100&max_price=600")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["price"] == 500.0

    async def test_list_products_sort(self, client: AsyncClient) -> None:
        """Test listing products with sorting."""
        # Create products with different prices
        await client.post(
            "/api/v1/products",
            json={"name": "Product Z", "category": "Books", "price": 100.0},
        )
        await client.post(
            "/api/v1/products",
            json={"name": "Product A", "category": "Books", "price": 50.0},
        )

        # Sort by name ascending
        response = await client.get("/api/v1/products?sort_by=name&sort_order=asc")

        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Product A"
        assert data["items"][1]["name"] == "Product Z"

    async def test_get_product(self, client: AsyncClient) -> None:
        """Test getting a product by ID."""
        # Create a product
        create_response = await client.post(
            "/api/v1/products",
            json={"name": "Test Product", "category": "Electronics", "price": 99.99},
        )
        product_id = create_response.json()["id"]

        # Get the product
        response = await client.get(f"/api/v1/products/{product_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Test Product"

    async def test_get_product_not_found(self, client: AsyncClient) -> None:
        """Test getting a non-existent product."""
        response = await client.get("/api/v1/products/00000000-0000-0000-0000-000000000000")

        assert response.status_code == 404

    async def test_update_product(self, client: AsyncClient) -> None:
        """Test updating a product."""
        # Create a product
        create_response = await client.post(
            "/api/v1/products",
            json={
                "name": "Original Name",
                "category": "Books",
                "price": 19.99,
                "discount": 5.0,
            },
        )
        product_id = create_response.json()["id"]

        # Update the product
        update_payload = {
            "name": "Updated Name",
            "price": 29.99,
            "discount": 15.0,
        }
        response = await client.put(f"/api/v1/products/{product_id}", json=update_payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["price"] == 29.99
        assert data["discount"] == 15.0
        assert data["category"] == "Books"  # Unchanged

    async def test_update_product_not_found(self, client: AsyncClient) -> None:
        """Test updating a non-existent product."""
        response = await client.put(
            "/api/v1/products/00000000-0000-0000-0000-000000000000",
            json={"name": "Updated Name"},
        )

        assert response.status_code == 404

    async def test_delete_product(self, client: AsyncClient) -> None:
        """Test deleting a product."""
        # Create a product
        create_response = await client.post(
            "/api/v1/products",
            json={"name": "To Delete", "category": "Food", "price": 15.0},
        )
        product_id = create_response.json()["id"]

        # Delete the product
        response = await client.delete(f"/api/v1/products/{product_id}")

        assert response.status_code == 204

        # Verify it's gone from list
        list_response = await client.get("/api/v1/products")
        data = list_response.json()
        assert data["total"] == 0

    async def test_delete_product_not_found(self, client: AsyncClient) -> None:
        """Test deleting a non-existent product."""
        response = await client.delete(
            "/api/v1/products/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404

    async def test_health_check(self, client: AsyncClient) -> None:
        """Test health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
