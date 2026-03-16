"""Product schemas."""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.constants import ProductCategory
from app.schemas.base import BaseProductSchema, TimestampedMixin
from app.utils import is_valid_url


class ProductCreateRequest(BaseProductSchema):
    """Product creation request schema."""

    category: ProductCategory = Field(
        ...,
        description="Product category from predefined list",
    )

    @field_validator("thumbnail_url")
    @classmethod
    def validate_thumbnail_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate thumbnail URL format."""
        if v and not is_valid_url(v):
            raise ValueError("Invalid thumbnail URL format")
        return v


class ProductUpdateRequest(BaseModel):
    """Product update request schema (all fields optional)."""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Product name",
    )
    category: Optional[ProductCategory] = Field(
        None,
        description="Product category",
    )
    description: Optional[str] = Field(
        None,
        max_length=5000,
        description="Product description",
    )
    thumbnail_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL to product thumbnail image",
    )
    price: Optional[float] = Field(
        None,
        gt=0,
        description="Product price",
    )
    discount: Optional[float] = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Discount percentage",
    )

    @field_validator("thumbnail_url")
    @classmethod
    def validate_thumbnail_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate thumbnail URL format."""
        if v and not is_valid_url(v):
            raise ValueError("Invalid thumbnail URL format")
        return v


class ProductResponse(BaseProductSchema, TimestampedMixin):
    """Product response schema."""

    id: str = Field(description="Product unique identifier (UUID)")

    class Config:
        """Pydantic config."""
        from_attributes = True


class ProductListResponse(BaseModel):
    """List of products response."""

    items: list[ProductResponse] = Field(description="List of products")
    total: int = Field(description="Total number of products")

    class Config:
        """Pydantic config."""
        from_attributes = True
