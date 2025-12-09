"""
Receipt Enums Module

Defines enumerations for receipt-related fields.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from enum import Enum


class ReceiptStatus(str, Enum):
    """
    Receipt status enumeration.

    States:
    - PENDING: Receipt uploaded, OCR not processed yet
    - PROCESSING: OCR is being processed
    - PROCESSED: OCR completed successfully
    - ERROR: OCR processing failed
    """

    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def list_values(cls) -> list[str]:
        """Get list of all status values."""
        return [status.value for status in cls]
