"""
Base Pydantic Models Module

Defines base schemas used across all entities.
Provides timestamp mixins and common field types.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class TimestampMixin(BaseModel):
    """
    Mixin for models with timestamp fields.

    Provides created_at and updated_at fields.
    """

    created_at: datetime = Field(
        ...,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )

    model_config = ConfigDict(from_attributes=True)


class BaseResponse(BaseModel):
    """
    Base response model with common fields.

    All response models should inherit from this.
    """

    id: str = Field(
        ...,
        description="UUID do registro"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    )


class PaginatedResponse(BaseModel):
    """
    Paginated response wrapper.

    Wraps list results with pagination metadata.

    Example:
        {
            "items": [...],
            "total": 100,
            "limit": 20,
            "offset": 0,
            "has_more": true
        }
    """

    items: list = Field(
        ...,
        description="List of items"
    )
    total: int = Field(
        ...,
        description="Total number of items",
        ge=0
    )
    limit: int = Field(
        ...,
        description="Number of items per page",
        ge=1,
        le=100
    )
    offset: int = Field(
        ...,
        description="Number of items skipped",
        ge=0
    )

    @property
    def has_more(self) -> bool:
        """Check if there are more items after current page."""
        return (self.offset + self.limit) < self.total

    @property
    def page(self) -> int:
        """Calculate current page number (1-indexed)."""
        return (self.offset // self.limit) + 1 if self.limit > 0 else 1

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        return (self.total + self.limit - 1) // self.limit if self.limit > 0 else 0

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [],
                "total": 100,
                "limit": 20,
                "offset": 0
            }
        }
    )


class SuccessResponse(BaseModel):
    """
    Generic success response.

    Used for operations that don't return data.

    Example:
        {
            "success": true,
            "message": "Operation completed successfully"
        }
    """

    success: bool = Field(
        default=True,
        description="Operation success status"
    )
    message: str = Field(
        ...,
        description="Success message"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully"
            }
        }
    )


class ErrorDetail(BaseModel):
    """
    Error detail model.

    Used in error responses.

    Example:
        {
            "code": "VALIDATION_ERROR",
            "message": "Invalid input data",
            "details": {"field": "email", "error": "Invalid format"}
        }
    """

    code: str = Field(
        ...,
        description="Error code"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    details: Optional[dict] = Field(
        default=None,
        description="Additional error details"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": {"field": "email"}
            }
        }
    )


class ErrorResponse(BaseModel):
    """
    Error response wrapper.

    Standardized error response format.

    Example:
        {
            "error": {
                "code": "NOT_FOUND",
                "message": "Resource not found",
                "details": {"resource_id": "123"}
            }
        }
    """

    error: ErrorDetail = Field(
        ...,
        description="Error details"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Resource not found",
                    "details": {}
                }
            }
        }
    )
