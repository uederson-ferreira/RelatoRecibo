"""
Report Update Models Module

Defines schema for updating existing reports.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.models.report.enums import ReportStatus


class ReportUpdate(BaseModel):
    """
    Schema for updating a report.

    All fields are optional.
    Only provided fields will be updated.

    Example:
        {
            "name": "Updated Report Name",
            "description": "Updated description",
            "status": "completed"
        }
    """

    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200,
        description="Nome do relatório"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Descrição do relatório"
    )
    start_date: Optional[date] = Field(
        None,
        description="Data de início"
    )
    end_date: Optional[date] = Field(
        None,
        description="Data final"
    )
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Observações"
    )
    status: Optional[ReportStatus] = Field(
        None,
        description="Status do relatório"
    )

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: Optional[date], info) -> Optional[date]:
        """Validate that end_date is after start_date."""
        if v and info.data.get("start_date"):
            if v < info.data["start_date"]:
                raise ValueError("end_date must be after or equal to start_date")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Report Name",
                "description": "Updated description",
                "status": "completed"
            }
        }
    )
