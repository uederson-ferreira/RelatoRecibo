"""
Report Response Models Module

Defines schemas for report API responses.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from decimal import Decimal
from typing import Optional
from pydantic import Field, ConfigDict

from app.models.base import BaseResponse, TimestampMixin
from app.models.report.base import ReportBase
from app.models.report.enums import ReportStatus


class ReportResponse(BaseResponse, ReportBase, TimestampMixin):
    """
    Complete report response schema.

    Includes all report fields plus computed values.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "user_id": "987fcdeb-51a2-43f7-8e6b-123456789abc",
            "name": "Viagem São Paulo - Janeiro 2025",
            "description": "Despesas da viagem de negócios",
            "start_date": "2025-01-15",
            "end_date": "2025-01-20",
            "notes": "Incluir recibos de hotel e transporte",
            "status": "draft",
            "total_value": 1250.50,
            "receipt_count": 8,
            "created_at": "2025-12-09T10:00:00Z",
            "updated_at": "2025-12-09T12:30:00Z"
        }
    """

    user_id: str = Field(
        ...,
        description="UUID do usuário dono do relatório"
    )
    status: ReportStatus = Field(
        default=ReportStatus.DRAFT,
        description="Status do relatório"
    )
    total_value: Decimal = Field(
        default=Decimal("0.00"),
        description="Valor total dos recibos (calculado automaticamente)",
        decimal_places=2
    )
    receipt_count: int = Field(
        default=0,
        description="Número de recibos no relatório",
        ge=0
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51a2-43f7-8e6b-123456789abc",
                "name": "Viagem São Paulo - Janeiro 2025",
                "description": "Despesas da viagem de negócios",
                "start_date": "2025-01-15",
                "end_date": "2025-01-20",
                "notes": "Incluir recibos de hotel e transporte",
                "status": "draft",
                "total_value": "1250.50",
                "receipt_count": 8,
                "created_at": "2025-12-09T10:00:00Z",
                "updated_at": "2025-12-09T12:30:00Z"
            }
        }
    )


class ReportSummary(BaseResponse):
    """
    Summary report schema for list views.

    Lighter version with key information only.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Viagem São Paulo - Janeiro 2025",
            "status": "draft",
            "total_value": 1250.50,
            "receipt_count": 8,
            "created_at": "2025-12-09T10:00:00Z"
        }
    """

    name: str = Field(
        ...,
        description="Nome do relatório"
    )
    status: ReportStatus = Field(
        ...,
        description="Status do relatório"
    )
    total_value: Decimal = Field(
        ...,
        description="Valor total",
        decimal_places=2
    )
    receipt_count: int = Field(
        ...,
        description="Número de recibos",
        ge=0
    )
    created_at: str = Field(
        ...,
        description="Data de criação"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Viagem São Paulo - Janeiro 2025",
                "status": "draft",
                "total_value": "1250.50",
                "receipt_count": 8,
                "created_at": "2025-12-09T10:00:00Z"
            }
        }
    )
