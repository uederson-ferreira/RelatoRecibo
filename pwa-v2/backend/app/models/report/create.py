"""
from __future__ import annotations
Report Create Models Module

Defines schema for creating new reports.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from pydantic import ConfigDict

from app.models.report.base import ReportBase


class ReportCreate(ReportBase):
    """
    Schema for creating a new report.

    Inherits all fields from ReportBase.
    User ID will be extracted from JWT token.

    Example:
        {
            "name": "Viagem São Paulo - Janeiro 2025",
            "description": "Despesas da viagem de negócios",
            "start_date": "2025-01-15",
            "end_date": "2025-01-20",
            "notes": "Incluir recibos de hotel e transporte"
        }
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Viagem São Paulo - Janeiro 2025",
                "description": "Despesas da viagem de negócios",
                "start_date": "2025-01-15",
                "end_date": "2025-01-20",
                "notes": "Incluir recibos de hotel e transporte"
            }
        }
    )
