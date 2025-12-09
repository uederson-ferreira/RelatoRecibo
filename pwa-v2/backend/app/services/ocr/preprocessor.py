"""
OCR Preprocessor Module

Prepares images for optimal OCR processing.
Applies filters, contrast adjustment, and noise reduction.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

import io
from typing import Tuple
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from loguru import logger


class OCRPreprocessor:
    """
    Prepares images for OCR processing.

    Features:
    - Grayscale conversion
    - Contrast enhancement
    - Noise reduction
    - Sharpening
    - Binarization (threshold)
    """

    @staticmethod
    def preprocess_image(image_data: bytes) -> bytes:
        """
        Apply preprocessing pipeline to image.

        Args:
            image_data: Original image binary data

        Returns:
            Preprocessed image binary data
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))

            # Convert to RGB if necessary
            if image.mode == "RGBA":
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            # Convert to grayscale
            image = image.convert("L")

            # Enhance contrast
            image = OCRPreprocessor._enhance_contrast(image)

            # Reduce noise
            image = OCRPreprocessor._reduce_noise(image)

            # Sharpen
            image = OCRPreprocessor._sharpen(image)

            # Optional: Apply thresholding for better text detection
            # image = OCRPreprocessor._apply_threshold(image)

            # Save to bytes
            output = io.BytesIO()
            image.save(output, format="PNG")
            output.seek(0)

            logger.debug("Image preprocessing completed")

            return output.read()

        except Exception as e:
            logger.warning(f"Error preprocessing image: {e}, returning original")
            # Return original if preprocessing fails
            return image_data

    @staticmethod
    def _enhance_contrast(image: Image.Image, factor: float = 1.5) -> Image.Image:
        """
        Enhance image contrast.

        Args:
            image: PIL Image
            factor: Contrast factor (1.0 = no change)

        Returns:
            Enhanced image
        """
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    @staticmethod
    def _reduce_noise(image: Image.Image) -> Image.Image:
        """
        Reduce image noise.

        Args:
            image: PIL Image

        Returns:
            Filtered image
        """
        # Apply median filter to reduce noise
        return image.filter(ImageFilter.MedianFilter(size=3))

    @staticmethod
    def _sharpen(image: Image.Image) -> Image.Image:
        """
        Sharpen image for better text detection.

        Args:
            image: PIL Image

        Returns:
            Sharpened image
        """
        return image.filter(ImageFilter.SHARPEN)

    @staticmethod
    def _apply_threshold(
        image: Image.Image,
        threshold: int = 128
    ) -> Image.Image:
        """
        Apply binary threshold to image.

        Args:
            image: PIL Image (grayscale)
            threshold: Threshold value (0-255)

        Returns:
            Binary image
        """
        # Convert to numpy array
        img_array = np.array(image)

        # Apply threshold
        binary = np.where(img_array > threshold, 255, 0).astype(np.uint8)

        # Convert back to PIL
        return Image.fromarray(binary)

    @staticmethod
    def resize_for_ocr(
        image_data: bytes,
        target_width: int = 1200
    ) -> bytes:
        """
        Resize image to optimal size for OCR.

        Args:
            image_data: Original image binary data
            target_width: Target width in pixels

        Returns:
            Resized image binary data
        """
        try:
            image = Image.open(io.BytesIO(image_data))

            # Only resize if larger than target
            if image.width > target_width:
                # Calculate new height maintaining aspect ratio
                aspect_ratio = image.height / image.width
                target_height = int(target_width * aspect_ratio)

                # Resize
                image = image.resize(
                    (target_width, target_height),
                    Image.Resampling.LANCZOS
                )

                logger.debug(f"Image resized to {target_width}x{target_height}")

            # Save to bytes
            output = io.BytesIO()
            image.save(output, format="PNG")
            output.seek(0)

            return output.read()

        except Exception as e:
            logger.warning(f"Error resizing image: {e}, returning original")
            return image_data
