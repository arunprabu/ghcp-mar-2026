"""Product repository (data access layer)."""

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductRepository:
    """Product data access layer."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create(self, product: Product) -> Product:
        """
        Create a new product.

        Args:
            product: Product instance to save

        Returns:
            Saved product instance
        """
        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        """
        Get product by ID (excluding soft-deleted).

        Args:
            product_id: Product UUID

        Returns:
            Product instance or None
        """
        query = select(Product).where(
            and_(
                Product.id == product_id,
                Product.is_deleted == False,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_all(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[List[Product], int]:
        """
        List all products with optional filtering and sorting.

        Args:
            category: Filter by category
            min_price: Filter by minimum price
            max_price: Filter by maximum price
            sort_by: Sort field (name, price, created_at)
            sort_order: Sort order (asc, desc)

        Returns:
            Tuple of (products list, total count)
        """
        # Build filters
        filters = [Product.is_deleted == False]

        if category:
            filters.append(Product.category == category)

        if min_price is not None:
            filters.append(Product.price >= min_price)

        if max_price is not None:
            filters.append(Product.price <= max_price)

        # Build query
        query = select(Product).where(and_(*filters))

        # Apply sorting
        sort_column = getattr(Product, sort_by, Product.name)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Get total count
        count_query = select(Product).where(and_(*filters))
        count_result = await self.session.execute(count_query)
        total = len(count_result.scalars().all())

        # Execute query
        result = await self.session.execute(query)
        products = result.scalars().all()

        return products, total

    async def update(self, product_id: str, **kwargs) -> Optional[Product]:
        """
        Update product fields.

        Args:
            product_id: Product UUID
            **kwargs: Fields to update

        Returns:
            Updated product or None if not found
        """
        product = await self.get_by_id(product_id)
        if not product:
            return None

        for key, value in kwargs.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)

        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def soft_delete(self, product_id: str) -> Optional[Product]:
        """
        Soft delete a product (mark as deleted).

        Args:
            product_id: Product UUID

        Returns:
            Deleted product or None if not found
        """
        product = await self.get_by_id(product_id)
        if not product:
            return None

        product.is_deleted = True
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def commit(self) -> None:
        """Commit transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback transaction."""
        await self.session.rollback()
