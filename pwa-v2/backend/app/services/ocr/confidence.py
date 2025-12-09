"""
OCR Confidence Calculator Module

Calculates confidence scores for OCR results.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import Dict, List
from loguru import logger


def calculate_confidence(ocr_data: Dict) -> float:
    """
    Calculate confidence score from Tesseract OCR data.

    Args:
        ocr_data: Dictionary from pytesseract.image_to_data()
                 Contains keys: conf, text, etc.

    Returns:
        Confidence score (0.0 to 1.0)
    """
    try:
        confidences = ocr_data.get('conf', [])
        texts = ocr_data.get('text', [])

        if not confidences or not texts:
            logger.warning("No confidence data available")
            return 0.0

        # Filter out empty texts and invalid confidences
        valid_confidences = []

        for conf, text in zip(confidences, texts):
            # Skip empty text
            if not text or not text.strip():
                continue

            # Skip invalid confidence values (-1 means no data)
            if conf == -1:
                continue

            # Tesseract confidence is 0-100
            valid_confidences.append(float(conf))

        if not valid_confidences:
            logger.warning("No valid confidence values found")
            return 0.0

        # Calculate average confidence
        avg_confidence = sum(valid_confidences) / len(valid_confidences)

        # Normalize to 0-1 scale
        normalized = avg_confidence / 100.0

        # Ensure between 0 and 1
        normalized = max(0.0, min(1.0, normalized))

        logger.debug(f"Confidence: {normalized:.2f} (from {len(valid_confidences)} words)")

        return round(normalized, 2)

    except Exception as e:
        logger.error(f"Error calculating confidence: {e}")
        return 0.0


def is_confidence_acceptable(confidence: float, threshold: float = 0.7) -> bool:
    """
    Check if confidence is above acceptable threshold.

    Args:
        confidence: Confidence score (0.0 to 1.0)
        threshold: Minimum acceptable confidence

    Returns:
        True if acceptable
    """
    return confidence >= threshold


def get_confidence_level(confidence: float) -> str:
    """
    Get human-readable confidence level.

    Args:
        confidence: Confidence score (0.0 to 1.0)

    Returns:
        Level string: "high", "medium", "low"
    """
    if confidence >= 0.8:
        return "high"
    elif confidence >= 0.6:
        return "medium"
    else:
        return "low"
