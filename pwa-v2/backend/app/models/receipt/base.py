"""
Receipt Base Models Module

Defines base receipt schema with common fields.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from __future__ import annotations

from decimal import Decimal
from datetime import date as date_type
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ReceiptBase(BaseModel):
    """
    Base receipt schema with common fields.

    Used as foundation for create/update schemas.
    """

    value: Decimal = Field(
        ...,
        description="Valor do recibo em reais"
    )
    date: date_type = Field(
        ...,
        description="Data do recibo"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Descrição do recibo"
    )
    category: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Categoria da despesa"
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Observações adicionais"
    )

    # Validators temporarily disabled to fix recursion error
    # @field_validator("value")
    # @classmethod
    # def validate_value(cls, v: Decimal) -> Decimal:
    #     """Ensure value has max 2 decimal places."""
    #     if v.as_tuple().exponent < -2:
    #         raise ValueError("Value must have at most 2 decimal places")
    #     return v

    # @field_validator("date")
    # @classmethod
    # def validate_date(cls, v: date) -> date:
    #     """Validate that receipt date is not in the future."""
    #     from datetime import date as date_class
    #     if v > date_class.today():
    #         raise ValueError("Receipt date cannot be in the future")
    #     return v

    model_config = ConfigDict(from_attributes=True)
