"""
from __future__ import annotations
Receipt Response Models Module

Defines schemas for receipt API responses.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from decimal import Decimal
from typing import Optional
from pydantic import Field, ConfigDict

from app.models.base import BaseResponse, TimestampMixin
from app.models.receipt.base import ReceiptBase
from app.models.receipt.enums import ReceiptStatus


class ReceiptResponse(BaseResponse, ReceiptBase, TimestampMixin):
    """
    Complete receipt response schema.

    Includes all receipt fields plus OCR data and image URLs.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "report_id": "987fcdeb-51a2-43f7-8e6b-123456789abc",
            "user_id": "456e4567-e89b-12d3-a456-426614174111",
            "value": 125.50,
            "date": "2025-01-15",
            "description": "Hotel - Noite de 15/01",
            "category": "Hospedagem",
            "notes": "Hotel Ibis - Centro",
            "status": "processed",
            "image_url": "https://...",
            "thumbnail_url": "https://...",
            "ocr_text": "HOTEL IBIS\\nVALOR: R$ 125,50\\n...",
            "ocr_confidence": 0.95,
            "created_at": "2025-12-09T10:00:00Z",
            "updated_at": "2025-12-09T10:05:00Z"
        }
    """

    report_id: str = Field(
        ...,
        description="UUID do relatório"
    )
    user_id: str = Field(
        ...,
        description="UUID do usuário"
    )
    status: ReceiptStatus = Field(
        default=ReceiptStatus.PENDING,
        description="Status do processamento OCR"
    )
    image_url: Optional[str] = Field(
        None,
        description="URL da imagem original do recibo"
    )
    thumbnail_url: Optional[str] = Field(
        None,
        description="URL da miniatura (thumbnail)"
    )
    ocr_text: Optional[str] = Field(
        None,
        description="Texto extraído por OCR"
    )
    ocr_confidence: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1,
        description="Confiança do OCR (0-1)"
    )
    ocr_error: Optional[str] = Field(
        None,
        description="Mensagem de erro do OCR (se houver)"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "report_id": "987fcdeb-51a2-43f7-8e6b-123456789abc",
                "user_id": "456e4567-e89b-12d3-a456-426614174111",
                "value": "125.50",
                "date": "2025-01-15",
                "description": "Hotel - Noite de 15/01",
                "category": "Hospedagem",
                "notes": "Hotel Ibis - Centro",
                "status": "processed",
                "image_url": "https://storage.example.com/receipts/123.jpg",
                "thumbnail_url": "https://storage.example.com/receipts/123_thumb.jpg",
                "ocr_text": "HOTEL IBIS\\nVALOR: R$ 125,50",
                "ocr_confidence": "0.95",
                "ocr_error": None,
                "created_at": "2025-12-09T10:00:00Z",
                "updated_at": "2025-12-09T10:05:00Z"
            }
        }
    )


class ReceiptSummary(BaseResponse):
    """
    Summary receipt schema for list views.

    Lighter version with key information only.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "value": 125.50,
            "date": "2025-01-15",
            "description": "Hotel - Noite de 15/01",
            "thumbnail_url": "https://...",
            "status": "processed"
        }
    """

    value: Decimal = Field(
        ...,
        description="Valor"
    )
    date: str = Field(
        ...,
        description="Data"
    )
    description: Optional[str] = Field(
        None,
        description="Descrição"
    )
    thumbnail_url: Optional[str] = Field(
        None,
        description="Miniatura"
    )
    status: ReceiptStatus = Field(
        ...,
        description="Status"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "value": "125.50",
                "date": "2025-01-15",
                "description": "Hotel - Noite de 15/01",
                "thumbnail_url": "https://storage.example.com/receipts/123_thumb.jpg",
                "status": "processed"
            }
        }
    )
