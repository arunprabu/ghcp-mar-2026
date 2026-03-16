"""Utilities and exceptions."""


class ProductNotFoundError(Exception):
    """Raised when a product is not found."""

    pass


class InvalidPriceError(Exception):
    """Raised when product price is invalid."""

    pass


class InvalidDiscountError(Exception):
    """Raised when product discount is invalid."""

    pass


class InvalidCategoryError(Exception):
    """Raised when product category is invalid."""

    pass


class ProductAlreadyDeletedError(Exception):
    """Raised when trying to operate on a deleted product."""

    pass
