"""
User Pydantic Models Module

Defines user-related schemas for authentication and profile.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict

from app.models.base import BaseResponse, TimestampMixin


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=200,
        description="User full name"
    )

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Schema for user registration.

    Example:
        {
            "email": "user@example.com",
            "password": "SecurePass123!",
            "full_name": "John Doe"
        }
    """

    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password (min 8 characters)"
    )
    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=200,
        description="User full name"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength.

        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "full_name": "John Doe"
            }
        }
    )


class UserLogin(BaseModel):
    """
    Schema for user login.

    Example:
        {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }
    """

    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    password: str = Field(
        ...,
        description="User password"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }
    )


class UserUpdate(BaseModel):
    """
    Schema for updating user profile.

    All fields are optional.

    Example:
        {
            "full_name": "John Updated Doe"
        }
    """

    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=200,
        description="User full name"
    )
    avatar_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL to user avatar image"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "John Updated Doe",
                "avatar_url": "https://example.com/avatar.jpg"
            }
        }
    )


class UserResponse(BaseResponse, TimestampMixin):
    """
    User response schema.

    Used for API responses. Excludes sensitive fields like password.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "email": "user@example.com",
            "full_name": "John Doe",
            "avatar_url": null,
            "email_verified": false,
            "created_at": "2025-12-09T10:00:00Z",
            "updated_at": "2025-12-09T10:00:00Z"
        }
    """

    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    full_name: Optional[str] = Field(
        None,
        description="User full name"
    )
    avatar_url: Optional[str] = Field(
        None,
        description="URL to user avatar image"
    )
    email_verified: bool = Field(
        default=False,
        description="Email verification status"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "avatar_url": None,
                "email_verified": False,
                "created_at": "2025-12-09T10:00:00Z",
                "updated_at": "2025-12-09T10:00:00Z"
            }
        }
    )


class TokenResponse(BaseModel):
    """
    JWT token response schema.

    Returned after successful login or registration.

    Example:
        {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "bearer",
            "expires_in": 86400,
            "user": {...}
        }
    """

    access_token: str = Field(
        ...,
        description="JWT access token"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type"
    )
    expires_in: int = Field(
        ...,
        description="Token expiration time in seconds",
        gt=0
    )
    user: UserResponse = Field(
        ...,
        description="User information"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "full_name": "John Doe",
                    "avatar_url": None,
                    "email_verified": False,
                    "created_at": "2025-12-09T10:00:00Z",
                    "updated_at": "2025-12-09T10:00:00Z"
                }
            }
        }
    )
