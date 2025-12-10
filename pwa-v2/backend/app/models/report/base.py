"""
Report Base Models Module

Defines base report schema with common fields.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from __future__ import annotations

from typing import Optional
from decimal import Decimal
from datetime import date as date_type
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models.report.enums import ReportStatus


class ReportBase(BaseModel):
    """
    Base report schema with common fields.

    Used as foundation for create/update schemas.
    """

    name: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Nome do relatório"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Descrição detalhada do relatório"
    )
    start_date: Optional[date_type] = Field(
        None,
        description="Data de início do período do relatório"
    )
    end_date: Optional[date_type] = Field(
        None,
        description="Data final do período do relatório"
    )
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Observações adicionais"
    )
    target_value: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Valor de meta do relatório (opcional)"
    )

    # Validator temporarily disabled to fix recursion error
    # @field_validator("end_date")
    # @classmethod
    # def validate_end_date(cls, v: Optional[date], info) -> Optional[date]:
    #     """Validate that end_date is after start_date."""
    #     if v and hasattr(info, 'data') and info.data.get("start_date"):
    #         if v < info.data["start_date"]:
    #             raise ValueError("end_date must be after or equal to start_date")
    #     return v

    model_config = ConfigDict(from_attributes=True)
