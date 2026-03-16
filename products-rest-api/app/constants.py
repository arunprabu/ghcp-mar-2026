"""Application constants."""

from enum import Enum


class ProductCategory(str, Enum):
    """Product category enumeration."""

    ELECTRONICS = "Electronics"
    CLOTHING = "Clothing"
    FOOD = "Food"
    HOME = "Home"
    SPORTS = "Sports"
    BOOKS = "Books"
    OTHER = "Other"


# API Configuration
API_V1_PREFIX = "/api/v1"
API_TITLE = "Products REST API"
API_VERSION = "1.0.0"
API_DESCRIPTION = "FastAPI-based REST API for managing products"

# Database
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10
DB_POOL_RECYCLE = 3600

# Pagination defaults (for future use)
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Validation
MIN_PRICE = 0.01
MAX_DISCOUNT = 100.0
MIN_DISCOUNT = 0.0
MAX_NAME_LENGTH = 255
MAX_DESCRIPTION_LENGTH = 5000
MAX_THUMBNAIL_URL_LENGTH = 500
