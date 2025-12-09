"""
OCR Extractor Module

Extracts text from receipt images using Tesseract OCR.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

import io
from typing import Dict, Optional, Tuple
from decimal import Decimal
from PIL import Image
import pytesseract
from loguru import logger

from app.utils.constants import OCR_LANGUAGES, OCR_TIMEOUT_SECONDS
from app.services.ocr.preprocessor import OCRPreprocessor
from app.services.ocr.value_parser import ValueParser
from app.services.ocr.confidence import calculate_confidence
from app.core.exceptions.receipt import OCRProcessingException


class OCRExtractor:
    """
    Extracts text and values from receipt images.

    Features:
    - Tesseract OCR integration
    - Portuguese and English support
    - Value extraction and parsing
    - Confidence calculation
    """

    def __init__(self):
        """Initialize OCR extractor."""
        self.preprocessor = OCRPreprocessor()
        self.value_parser = ValueParser()
        self.languages = "+".join(OCR_LANGUAGES)  # "por+eng"

    async def extract_receipt_data(
        self,
        image_data: bytes
    ) -> Dict[str, any]:
        """
        Extract text and value from receipt image.

        Args:
            image_data: Receipt image binary data

        Returns:
            Dictionary with OCR results:
            {
                "text": "extracted text",
                "value": Decimal("123.45"),
                "confidence": 0.95
            }

        Raises:
            OCRProcessingException: If OCR fails
        """
        try:
            logger.info("Starting OCR extraction")

            # Preprocess image
            preprocessed = self.preprocessor.preprocess_image(image_data)

            # Extract text with Tesseract
            text, confidence = await self._extract_text(preprocessed)

            if not text or len(text.strip()) < 10:
                logger.warning("OCR returned insufficient text")
                raise OCRProcessingException(
                    details={
                        "error": "Insufficient text extracted",
                        "text_length": len(text) if text else 0
                    }
                )

            # Parse value from text
            value = self.value_parser.extract_value(text)

            logger.info(f"OCR completed: {len(text)} chars, value: {value}, confidence: {confidence}")

            return {
                "text": text.strip(),
                "value": value,
                "confidence": confidence
            }

        except OCRProcessingException:
            raise
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise OCRProcessingException(
                details={"error": str(e)}
            )

    async def _extract_text(
        self,
        image_data: bytes
    ) -> Tuple[str, float]:
        """
        Extract text from image using Tesseract.

        Args:
            image_data: Preprocessed image binary data

        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))

            # Configure Tesseract
            config = self._get_tesseract_config()

            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=self.languages,
                config=config,
                timeout=OCR_TIMEOUT_SECONDS
            )

            # Get detailed OCR data for confidence calculation
            data = pytesseract.image_to_data(
                image,
                lang=self.languages,
                config=config,
                timeout=OCR_TIMEOUT_SECONDS,
                output_type=pytesseract.Output.DICT
            )

            # Calculate confidence
            confidence = calculate_confidence(data)

            return text, confidence

        except pytesseract.TesseractNotFoundError:
            logger.error("Tesseract not installed or not in PATH")
            raise OCRProcessingException(
                details={
                    "error": "Tesseract OCR not found",
                    "message": "Install Tesseract: apt-get install tesseract-ocr tesseract-ocr-por"
                }
            )
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            raise

    def _get_tesseract_config(self) -> str:
        """
        Get Tesseract configuration string.

        Returns:
            Configuration string for pytesseract
        """
        # PSM (Page Segmentation Mode):
        # 3 = Fully automatic page segmentation, but no OSD (default)
        # 6 = Assume a single uniform block of text
        # 11 = Sparse text. Find as much text as possible in no particular order

        # OEM (OCR Engine Mode):
        # 3 = Default, based on what is available (LSTM + Legacy)

        return "--psm 3 --oem 3"

    async def extract_text_only(self, image_data: bytes) -> str:
        """
        Extract only text without parsing value.

        Args:
            image_data: Receipt image binary data

        Returns:
            Extracted text
        """
        preprocessed = self.preprocessor.preprocess_image(image_data)
        text, _ = await self._extract_text(preprocessed)
        return text.strip()

    async def verify_tesseract(self) -> bool:
        """
        Verify Tesseract installation.

        Returns:
            True if Tesseract is available
        """
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
            return True
        except:
            logger.error("Tesseract not available")
            return False
