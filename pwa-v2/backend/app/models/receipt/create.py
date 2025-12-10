"""
from __future__ import annotations
Receipt Create Models Module

Defines schema for creating new receipts.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from pydantic import Field, ConfigDict

from app.models.receipt.base import ReceiptBase


class ReceiptCreate(ReceiptBase):
    """
    Schema for creating a new receipt.

    Inherits all fields from ReceiptBase.
    Report ID is required to associate receipt with a report.

    Example:
        {
            "report_id": "123e4567-e89b-12d3-a456-426614174000",
            "value": 125.50,
            "date": "2025-01-15",
            "description": "Hotel - Noite de 15/01",
            "category": "Hospedagem",
            "notes": "Hotel Ibis - Centro"
        }
    """

    report_id: str = Field(
        ...,
        description="UUID do relatório ao qual o recibo pertence"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "report_id": "123e4567-e89b-12d3-a456-426614174000",
                "value": 125.50,
                "date": "2025-01-15",
                "description": "Hotel - Noite de 15/01",
                "category": "Hospedagem",
                "notes": "Hotel Ibis - Centro"
            }
        }
    )
