"""Base schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TimestampedMixin(BaseModel):
    """Mixin for models with timestamps."""

    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        """Pydantic config."""
        from_attributes = True


class BaseProductSchema(BaseModel):
    """Base product schema with common fields."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Product name",
    )
    category: str = Field(
        ...,
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
    price: float = Field(
        ...,
        gt=0,
        description="Product price (must be > 0)",
    )
    discount: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Discount percentage (0-100)",
    )

    class Config:
        """Pydantic config."""
        from_attributes = True
