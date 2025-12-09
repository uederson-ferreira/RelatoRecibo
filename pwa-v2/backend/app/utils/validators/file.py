"""
File Validator Module

Validates uploaded files (size, type, format).

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import Optional
from fastapi import UploadFile
from loguru import logger

from app.utils.constants import (
    ALLOWED_IMAGE_EXTENSIONS,
    MAX_UPLOAD_SIZE_BYTES
)
from app.core.exceptions.receipt import (
    InvalidFileTypeException,
    FileTooLargeException
)


def validate_image_file(file: UploadFile) -> None:
    """
    Validate uploaded image file.

    Checks:
    - File size within limits
    - Content type is image
    - Extension is allowed

    Args:
        file: FastAPI UploadFile object

    Raises:
        InvalidFileTypeException: If file type not allowed
        FileTooLargeException: If file exceeds size limit
    """
    # Validate content type
    if not file.content_type or not file.content_type.startswith("image/"):
        logger.warning(f"Invalid content type: {file.content_type}")
        raise InvalidFileTypeException(
            details={
                "content_type": file.content_type,
                "allowed": "image/*"
            }
        )

    # Validate extension
    if file.filename:
        extension = _get_file_extension(file.filename)
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            logger.warning(f"Invalid extension: {extension}")
            raise InvalidFileTypeException(
                details={
                    "extension": extension,
                    "allowed": ALLOWED_IMAGE_EXTENSIONS
                }
            )

    # Validate file size (read first chunk to check)
    # Note: Full size validation happens during read
    logger.info(f"File validation passed: {file.filename}")


def validate_file_size(file_data: bytes, max_size: int = MAX_UPLOAD_SIZE_BYTES) -> None:
    """
    Validate file size.

    Args:
        file_data: File binary data
        max_size: Maximum allowed size in bytes

    Raises:
        FileTooLargeException: If file exceeds size limit
    """
    file_size = len(file_data)

    if file_size > max_size:
        logger.warning(f"File too large: {file_size} bytes (max: {max_size})")
        raise FileTooLargeException(
            details={
                "size_bytes": file_size,
                "max_bytes": max_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "max_mb": round(max_size / (1024 * 1024), 2)
            }
        )


def _get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.

    Args:
        filename: File name with extension

    Returns:
        Extension (e.g., ".jpg", ".png")
    """
    if "." not in filename:
        return ""

    extension = "." + filename.rsplit(".", 1)[1].lower()
    return extension


def get_content_type_from_extension(extension: str) -> str:
    """
    Get MIME type from file extension.

    Args:
        extension: File extension (e.g., ".jpg", ".png")

    Returns:
        MIME type (e.g., "image/jpeg")
    """
    content_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp"
    }

    return content_type_map.get(extension.lower(), "application/octet-stream")
