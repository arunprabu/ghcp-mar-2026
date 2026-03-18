"""Product API routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import ProductCategory, API_V1_PREFIX, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.database import get_session
from app.schemas.product import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductListResponse,
    ProductDeleteResponse,
)
from app.services.product_service import ProductService
from app.utils.exceptions import (
    ProductNotFoundError,
    InvalidPriceError,
    InvalidDiscountError,
)

router = APIRouter(prefix=f"{API_V1_PREFIX}/products", tags=["products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
async def create_product(
    request: ProductCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> ProductResponse:
    """
    Create a new product.

    - **name**: Product name (required, max 255 chars)
    - **category**: Product category from predefined list (required)
    - **price**: Product price (required, must be > 0)
    - **description**: Product description (optional)
    - **thumbnail_url**: URL to product image (optional)
    - **discount**: Discount percentage 0-100 (optional, default 0)
    """
    try:
        service = ProductService(session)
        product = await service.create_product(
            name=request.name,
            category=request.category,
            description=request.description,
            thumbnail_url=request.thumbnail_url,
            price=request.price,
            discount=request.discount,
        )
        return ProductResponse.model_validate(product)
    except (InvalidPriceError, InvalidDiscountError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List all products",
)
async def list_products(
    category: Optional[ProductCategory] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"Items per page (max {MAX_PAGE_SIZE})",
    ),
    session: AsyncSession = Depends(get_session),
) -> ProductListResponse:
    """
    List all products with optional filtering, sorting, and pagination.

    - **category**: Filter by product category (optional)
    - **min_price**: Filter by minimum price (optional)
    - **max_price**: Filter by maximum price (optional)
    - **sort_by**: Sort field: name, price, created_at (default: name)
    - **sort_order**: Sort order: asc, desc (default: asc)
    - **page**: Page number, starting at 1 (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    """
    service = ProductService(session)
    products, total = await service.list_products(
        category=category.value if category else None,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    return ProductListResponse(
        items=[ProductResponse.model_validate(product) for product in products],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
)
async def get_product(
    product_id: str,
    session: AsyncSession = Depends(get_session),
) -> ProductResponse:
    """
    Get a specific product by its ID.

    - **product_id**: Product UUID (required)
    """
    try:
        service = ProductService(session)
        product = await service.get_product(product_id)
        return ProductResponse.model_validate(product)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
)
async def update_product(
    product_id: str,
    request: ProductUpdateRequest,
    session: AsyncSession = Depends(get_session),
) -> ProductResponse:
    """
    Update an existing product (full or partial update).

    - **product_id**: Product UUID (required)
    - **request body**: Fields to update (all optional)
    """
    try:
        service = ProductService(session)
        product = await service.update_product(
            product_id=product_id,
            name=request.name,
            category=request.category,
            description=request.description,
            thumbnail_url=request.thumbnail_url,
            price=request.price,
            discount=request.discount,
        )
        return ProductResponse.model_validate(product)
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except (InvalidPriceError, InvalidDiscountError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete(
    "/{product_id}",
    response_model=ProductDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete product (soft delete)",
)
async def delete_product(
    product_id: str,
    session: AsyncSession = Depends(get_session),
) -> ProductDeleteResponse:
    """
    Soft delete a product (mark as deleted, not removed from DB).

    - **product_id**: Product UUID (required)
    """
    try:
        service = ProductService(session)
        await service.delete_product(product_id)
        return ProductDeleteResponse(
            message=f"Product with id {product_id} deleted successfully"
        )
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
