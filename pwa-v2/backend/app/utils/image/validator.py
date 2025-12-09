"""
Image Validator Module

Validates image content and properties.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

import io
from PIL import Image
from loguru import logger

from app.utils.constants import MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT
from app.core.exceptions.receipt import InvalidImageException


def validate_image_content(image_data: bytes) -> Image.Image:
    """
    Validate image can be opened and processed.

    Args:
        image_data: Image binary data

    Returns:
        PIL Image object

    Raises:
        InvalidImageException: If image is corrupted or invalid
    """
    try:
        image = Image.open(io.BytesIO(image_data))

        # Verify image
        image.verify()

        # Re-open after verify (verify closes the image)
        image = Image.open(io.BytesIO(image_data))

        logger.info(f"Image validated: {image.format} {image.size} {image.mode}")

        return image

    except Exception as e:
        logger.error(f"Invalid image: {e}")
        raise InvalidImageException(
            details={"error": str(e)}
        )


def validate_image_dimensions(image: Image.Image) -> None:
    """
    Validate image dimensions are within limits.

    Args:
        image: PIL Image object

    Raises:
        InvalidImageException: If dimensions exceed limits
    """
    width, height = image.size

    if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
        logger.warning(f"Image dimensions too large: {width}x{height}")
        raise InvalidImageException(
            details={
                "width": width,
                "height": height,
                "max_width": MAX_IMAGE_WIDTH,
                "max_height": MAX_IMAGE_HEIGHT
            }
        )

    if width < 100 or height < 100:
        logger.warning(f"Image dimensions too small: {width}x{height}")
        raise InvalidImageException(
            details={
                "width": width,
                "height": height,
                "min_width": 100,
                "min_height": 100,
                "message": "Image is too small for OCR processing"
            }
        )


def is_image_valid(image_data: bytes) -> bool:
    """
    Check if image data is valid without raising exceptions.

    Args:
        image_data: Image binary data

    Returns:
        True if valid, False otherwise
    """
    try:
        validate_image_content(image_data)
        return True
    except:
        return False
