"""
Profile Schemas Module

Pydantic schemas for profile endpoints.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class ProfileUpdate(BaseModel):
    """
    Schema for updating user profile.

    All fields are optional.
    """

    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=200,
        description="Nome completo do usuário"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Email do usuário (deve ser único)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "João Silva",
                "email": "joao@example.com"
            }
        }
    )


class ProfileResponse(BaseModel):
    """
    Schema for profile response.
    """

    id: str = Field(..., description="UUID do usuário")
    email: str = Field(..., description="Email do usuário")
    full_name: Optional[str] = Field(None, description="Nome completo")
    avatar_url: Optional[str] = Field(None, description="URL do avatar")
    created_at: str = Field(..., description="Data de criação")
    updated_at: str = Field(..., description="Data de atualização")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "joao@example.com",
                "full_name": "João Silva",
                "avatar_url": "https://storage.example.com/avatars/123.jpg",
                "created_at": "2025-12-09T10:00:00Z",
                "updated_at": "2025-12-09T10:00:00Z"
            }
        }
    )


class UserStatsResponse(BaseModel):
    """
    Schema for user statistics response.
    """

    total_reports: int = Field(0, description="Total de relatórios")
    total_receipts: int = Field(0, description="Total de recibos")
    total_value: float = Field(0.0, description="Valor total de todos os recibos")
    reports_by_status: dict = Field(
        default_factory=dict,
        description="Contagem de relatórios por status"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_reports": 10,
                "total_receipts": 45,
                "total_value": 5432.10,
                "reports_by_status": {
                    "draft": 5,
                    "completed": 3,
                    "archived": 2
                }
            }
        }
    )
