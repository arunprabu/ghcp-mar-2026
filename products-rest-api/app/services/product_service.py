"""Product service (business logic layer)."""

from typing import Optional, List
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ProductCategory
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.utils.exceptions import (
    ProductNotFoundError,
    InvalidPriceError,
    InvalidDiscountError,
)


class ProductService:
    """Product business logic service."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service with database session."""
        self.repository = ProductRepository(session)

    async def create_product(
        self,
        name: str,
        category: ProductCategory,
        price: float,
        description: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        discount: float = 0.0,
    ) -> Product:
        """
        Create a new product.

        Args:
            name: Product name
            category: Product category
            price: Product price
            description: Product description
            thumbnail_url: Thumbnail URL
            discount: Discount percentage

        Returns:
            Created product

        Raises:
            InvalidPriceError: If price is invalid
            InvalidDiscountError: If discount is invalid
        """
        # Validate price
        if price <= 0:
            raise InvalidPriceError("Price must be greater than 0")

        # Validate discount
        if not (0 <= discount <= 100):
            raise InvalidDiscountError("Discount must be between 0 and 100")

        # Create product
        product = Product(
            id=str(uuid4()),
            name=name,
            category=category.value,
            description=description,
            thumbnail_url=thumbnail_url,
            price=price,
            discount=discount,
        )

        created_product = await self.repository.create(product)
        await self.repository.commit()

        return created_product

    async def get_product(self, product_id: str) -> Product:
        """
        Get product by ID.

        Args:
            product_id: Product UUID

        Returns:
            Product instance

        Raises:
            ProductNotFoundError: If product not found
        """
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")
        return product

    async def list_products(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[List[Product], int]:
        """
        List all products with filtering, sorting, and pagination.

        Args:
            category: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            sort_by: Sort field
            sort_order: Sort order (asc/desc)
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            Tuple of (products, total count)
        """
        offset = (page - 1) * page_size
        return await self.repository.list_all(
            category=category,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=page_size,
            offset=offset,
        )

    async def update_product(
        self,
        product_id: str,
        name: Optional[str] = None,
        category: Optional[ProductCategory] = None,
        description: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        price: Optional[float] = None,
        discount: Optional[float] = None,
    ) -> Product:
        """
        Update product fields.

        Args:
            product_id: Product UUID
            name: New name
            category: New category
            description: New description
            thumbnail_url: New thumbnail URL
            price: New price
            discount: New discount

        Returns:
            Updated product

        Raises:
            ProductNotFoundError: If product not found
            InvalidPriceError: If price is invalid
            InvalidDiscountError: If discount is invalid
        """
        # Validate price if provided
        if price is not None and price <= 0:
            raise InvalidPriceError("Price must be greater than 0")

        # Validate discount if provided
        if discount is not None and not (0 <= discount <= 100):
            raise InvalidDiscountError("Discount must be between 0 and 100")

        # Prepare update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if category is not None:
            update_data["category"] = category.value
        if description is not None:
            update_data["description"] = description
        if thumbnail_url is not None:
            update_data["thumbnail_url"] = thumbnail_url
        if price is not None:
            update_data["price"] = price
        if discount is not None:
            update_data["discount"] = discount

        product = await self.repository.update(product_id, **update_data)
        if not product:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")

        await self.repository.commit()
        return product

    async def delete_product(self, product_id: str) -> Product:
        """
        Soft delete a product.

        Args:
            product_id: Product UUID

        Returns:
            Deleted product

        Raises:
            ProductNotFoundError: If product not found
        """
        product = await self.repository.soft_delete(product_id)
        if not product:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")

        await self.repository.commit()
        return product
