"""
Receipt Exception Module

Defines receipt-specific exceptions.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import Optional, Dict, Any

from app.core.exceptions.base import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ValidationException
)


class ReceiptNotFoundException(NotFoundException):
    """
    Raised when receipt is not found.

    Example:
        raise ReceiptNotFoundException(
            details={"receipt_id": "123e4567-e89b-12d3-a456-426614174000"}
        )
    """

    def __init__(
        self,
        message: str = "Receipt not found",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="RECEIPT_NOT_FOUND",
            details=details
        )


class ReceiptAccessDeniedException(ForbiddenException):
    """
    Raised when user tries to access receipt they don't own.

    Example:
        raise ReceiptAccessDeniedException(
            details={
                "receipt_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51a2-43f7-8e6b-123456789abc"
            }
        )
    """

    def __init__(
        self,
        message: str = "You don't have access to this receipt",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="RECEIPT_ACCESS_DENIED",
            details=details
        )


class InvalidFileTypeException(BadRequestException):
    """
    Raised when uploaded file type is not allowed.

    Example:
        raise InvalidFileTypeException(
            details={
                "provided_type": ".pdf",
                "allowed_types": [".jpg", ".jpeg", ".png", ".webp"]
            }
        )
    """

    def __init__(
        self,
        message: str = "Invalid file type",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="INVALID_FILE_TYPE",
            details=details
        )


class FileTooLargeException(BadRequestException):
    """
    Raised when uploaded file exceeds size limit.

    Example:
        raise FileTooLargeException(
            details={
                "file_size": 10485760,  # 10MB
                "max_size": 5242880     # 5MB
            }
        )
    """

    def __init__(
        self,
        message: str = "File size exceeds maximum allowed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="FILE_TOO_LARGE",
            details=details
        )


class InvalidImageException(ValidationException):
    """
    Raised when uploaded file is not a valid image.

    Example:
        raise InvalidImageException(
            message="File is corrupted or not a valid image",
            details={"filename": "receipt.jpg"}
        )
    """

    def __init__(
        self,
        message: str = "Invalid image file",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="INVALID_IMAGE",
            details=details
        )


class OCRProcessingException(ValidationException):
    """
    Raised when OCR processing fails.

    Example:
        raise OCRProcessingException(
            message="Failed to extract text from image",
            details={"error": "Low image quality"}
        )
    """

    def __init__(
        self,
        message: str = "OCR processing failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="OCR_PROCESSING_FAILED",
            details=details
        )


class InvalidReceiptValueException(ValidationException):
    """
    Raised when receipt value is invalid.

    Example:
        raise InvalidReceiptValueException(
            message="Value must be greater than zero",
            details={"provided_value": -10.00}
        )
    """

    def __init__(
        self,
        message: str = "Invalid receipt value",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="INVALID_RECEIPT_VALUE",
            details=details
        )


class InvalidReceiptDateException(ValidationException):
    """
    Raised when receipt date is invalid.

    Example:
        raise InvalidReceiptDateException(
            message="Receipt date cannot be in the future",
            details={"provided_date": "2026-12-31"}
        )
    """

    def __init__(
        self,
        message: str = "Invalid receipt date",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="INVALID_RECEIPT_DATE",
            details=details
        )


class StorageUploadException(ValidationException):
    """
    Raised when file upload to storage fails.

    Example:
        raise StorageUploadException(
            message="Failed to upload file to storage",
            details={"bucket": "receipts", "error": "Connection timeout"}
        )
    """

    def __init__(
        self,
        message: str = "Failed to upload file",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="STORAGE_UPLOAD_FAILED",
            details=details
        )


class ImageProcessingException(ValidationException):
    """
    Raised when image processing/optimization fails.

    Example:
        raise ImageProcessingException(
            message="Failed to optimize image",
            details={"operation": "resize", "error": "Invalid dimensions"}
        )
    """

    def __init__(
        self,
        message: str = "Image processing failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="IMAGE_PROCESSING_FAILED",
            details=details
        )
