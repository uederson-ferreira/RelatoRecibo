"""
Application Settings Module

Centralized configuration using Pydantic Settings.
Environment variables are loaded from .env file.
All settings are validated at startup.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are validated using Pydantic.
    Missing required settings will raise an error at startup.

    Usage:
        from app.config import settings

        print(settings.SUPABASE_URL)
        print(settings.MAX_UPLOAD_SIZE)
    """

    # ----------------------------------------
    # Application Settings
    # ----------------------------------------
    PROJECT_NAME: str = Field(
        default="RelatoRecibo API",
        description="Nome do projeto"
    )
    VERSION: str = Field(
        default="2.0.0",
        description="Versão da API"
    )
    ENVIRONMENT: str = Field(
        default="development",
        description="Ambiente: development, staging, production"
    )
    DEBUG: bool = Field(
        default=True,
        description="Enable debug mode"
    )

    # ----------------------------------------
    # API Configuration
    # ----------------------------------------
    API_V1_PREFIX: str = Field(
        default="/api/v1",
        description="API version 1 prefix"
    )
    HOST: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    PORT: int = Field(
        default=8000,
        description="Server port"
    )
    RELOAD: bool = Field(
        default=True,
        description="Enable auto-reload (dev only)"
    )

    # ----------------------------------------
    # CORS Settings
    # ----------------------------------------
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://localhost:8000"
        ],
        description="Lista de origins permitidas para CORS"
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse ALLOWED_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ----------------------------------------
    # Supabase Configuration
    # ----------------------------------------
    SUPABASE_URL: str = Field(
        ...,
        description="Supabase project URL"
    )
    SUPABASE_ANON_KEY: str = Field(
        ...,
        description="Supabase anon/public key"
    )
    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        ...,
        description="Supabase service role key (backend only)"
    )

    # ----------------------------------------
    # JWT / Authentication
    # ----------------------------------------
    JWT_SECRET_KEY: str = Field(
        ...,
        description="Secret key for JWT token signing"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=1440,  # 24 hours
        description="Access token expiration time in minutes"
    )

    # ----------------------------------------
    # File Upload Settings
    # ----------------------------------------
    MAX_UPLOAD_SIZE: int = Field(
        default=5 * 1024 * 1024,  # 5MB
        description="Maximum file upload size in bytes"
    )
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".webp"],
        description="Allowed file extensions for upload"
    )
    UPLOAD_DIR: str = Field(
        default="uploads",
        description="Directory for temporary file uploads"
    )

    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v):
        """Parse ALLOWED_EXTENSIONS from comma-separated string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    # ----------------------------------------
    # OCR Configuration
    # ----------------------------------------
    TESSERACT_LANG: str = Field(
        default="por",
        description="Tesseract language (por = Portuguese)"
    )
    OCR_TIMEOUT: int = Field(
        default=30,
        description="OCR processing timeout in seconds"
    )
    TESSERACT_PATH: str = Field(
        default="/usr/bin/tesseract",
        description="Path to tesseract binary"
    )

    # ----------------------------------------
    # Storage Configuration
    # ----------------------------------------
    STORAGE_BUCKET_NAME: str = Field(
        default="receipts",
        description="Supabase storage bucket name"
    )
    STORAGE_MAX_FILE_SIZE: int = Field(
        default=5 * 1024 * 1024,  # 5MB
        description="Maximum file size for storage"
    )

    # ----------------------------------------
    # Rate Limiting
    # ----------------------------------------
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Maximum requests per minute per user"
    )

    # ----------------------------------------
    # Logging Configuration
    # ----------------------------------------
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    LOG_FILE: str = Field(
        default="logs/app.log",
        description="Log file path"
    )
    LOG_ROTATION: str = Field(
        default="500 MB",
        description="Log rotation size"
    )
    LOG_RETENTION: str = Field(
        default="10 days",
        description="Log retention period"
    )

    # ----------------------------------------
    # Pydantic Config
    # ----------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # ----------------------------------------
    # Computed Properties
    # ----------------------------------------
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"

    @property
    def docs_url(self) -> str:
        """Get docs URL (None in production)."""
        return "/api/docs" if not self.is_production else None

    @property
    def redoc_url(self) -> str:
        """Get redoc URL (None in production)."""
        return "/api/redoc" if not self.is_production else None


# ----------------------------------------
# Global settings instance
# ----------------------------------------
settings = Settings()
