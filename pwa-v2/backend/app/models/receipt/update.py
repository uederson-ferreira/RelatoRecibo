"""
Receipt Update Models Module

Defines schema for updating existing receipts.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from decimal import Decimal
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ReceiptUpdate(BaseModel):
    """
    Schema for updating a receipt.

    All fields are optional.
    Only provided fields will be updated.

    Example:
        {
            "value": 150.00,
            "description": "Hotel - Noite de 15/01 (atualizado)",
            "category": "Hospedagem"
        }
    """

    value: Optional[Decimal] = Field(
        None,
        gt=0,
        decimal_places=2,
        description="Valor do recibo"
    )
    date: Optional[date] = Field(
        None,
        description="Data do recibo"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Descrição"
    )
    category: Optional[str] = Field(
        None,
        max_length=100,
        description="Categoria"
    )
    notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Observações"
    )

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Ensure value has max 2 decimal places."""
        if v and v.as_tuple().exponent < -2:
            raise ValueError("Value must have at most 2 decimal places")
        return v

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: Optional[date]) -> Optional[date]:
        """Validate that receipt date is not in the future."""
        if v:
            from datetime import date as date_class
            if v > date_class.today():
                raise ValueError("Receipt date cannot be in the future")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "value": 150.00,
                "description": "Hotel - Noite de 15/01 (atualizado)",
                "category": "Hospedagem"
            }
        }
    )
