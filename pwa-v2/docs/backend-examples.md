# Backend FastAPI - Exemplos de Código

Este documento contém exemplos práticos de implementação do backend FastAPI para o RelatoRecibo.

## 1. Estrutura Principal - `app/main.py`

```python
"""
RelatoRecibo Backend API
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api.v1.router import api_router
from app.config import settings
from app.core.exceptions import AppException

# Configure logger
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para gestão de recibos e relatórios com OCR",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "RelatoRecibo API",
        "version": settings.VERSION,
        "docs": "/api/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Only for development
    )
```

## 2. Configurações - `app/config.py`

```python
"""
Application settings using Pydantic BaseSettings
Environment variables are loaded from .env file
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "RelatoRecibo API"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        env="ALLOWED_ORIGINS"
    )

    # Supabase
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(..., env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")

    # JWT
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # File Upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp"]
    UPLOAD_DIR: str = "uploads"

    # OCR
    TESSERACT_LANG: str = "por"  # Portuguese
    OCR_TIMEOUT: int = 30  # seconds

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

## 3. Modelos Pydantic - `app/models/receipt.py`

```python
"""
Pydantic models for Receipt
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class ReceiptStatus(str, Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    ERROR = "error"


class ReceiptBase(BaseModel):
    """Base receipt schema"""
    value: Decimal = Field(..., gt=0, description="Valor do recibo")
    date: date = Field(default_factory=date.today, description="Data do recibo")
    description: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)

    @validator('value')
    def validate_value(cls, v):
        """Ensure value has max 2 decimal places"""
        if v.as_tuple().exponent < -2:
            raise ValueError('Value must have at most 2 decimal places')
        return v


class ReceiptCreate(ReceiptBase):
    """Schema for creating a receipt"""
    report_id: str = Field(..., description="UUID do relatório")


class ReceiptUpdate(BaseModel):
    """Schema for updating a receipt"""
    value: Optional[Decimal] = Field(None, gt=0)
    date: Optional[date] = None
    description: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)


class ReceiptResponse(ReceiptBase):
    """Schema for receipt response"""
    id: str
    report_id: str
    user_id: str
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[Decimal] = None
    ocr_status: ReceiptStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReceiptWithReport(ReceiptResponse):
    """Receipt with report info"""
    report_name: str
    report_status: str
```

## 4. Serviço OCR - `app/services/ocr_service.py`

```python
"""
OCR Service using Tesseract
"""
import re
from decimal import Decimal
from typing import Optional, Tuple
from PIL import Image
import pytesseract
from loguru import logger

from app.config import settings


class OCRService:
    """Service for OCR processing"""

    @staticmethod
    async def extract_text(image_path: str) -> str:
        """
        Extract text from image using Tesseract OCR

        Args:
            image_path: Path to image file

        Returns:
            Extracted text
        """
        try:
            image = Image.open(image_path)

            # Preprocessing for better OCR results
            image = image.convert('L')  # Convert to grayscale

            # Run OCR
            text = pytesseract.image_to_string(
                image,
                lang=settings.TESSERACT_LANG,
                timeout=settings.OCR_TIMEOUT
            )

            logger.info(f"OCR completed for {image_path}")
            return text.strip()

        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {str(e)}")
            raise

    @staticmethod
    def extract_value(text: str) -> Optional[Decimal]:
        """
        Extract monetary value from OCR text

        Patterns matched:
        - R$ 123,45
        - R$ 1.234,56
        - Total: R$ 123,45
        - Valor: 123,45

        Args:
            text: OCR extracted text

        Returns:
            Extracted value or None
        """
        # Patterns to match Brazilian currency
        patterns = [
            r'R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})',  # R$ 1.234,56
            r'R\$\s*(\d+,\d{2})',                   # R$ 123,45
            r'total[:\s]+R\$\s*(\d{1,3}(?:\.\d{3})*,\d{2})',  # Total: R$ 1.234,56
            r'valor[:\s]+(\d{1,3}(?:\.\d{3})*,\d{2})',        # Valor: 1.234,56
            r'(\d{1,3}(?:\.\d{3})*,\d{2})',         # 1.234,56
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1)
                # Convert Brazilian format to Decimal
                value_str = value_str.replace('.', '').replace(',', '.')
                try:
                    return Decimal(value_str)
                except:
                    continue

        return None

    @staticmethod
    def calculate_confidence(text: str, extracted_value: Optional[Decimal]) -> Decimal:
        """
        Calculate OCR confidence score (0-100)

        Simple heuristic based on:
        - Text length
        - Presence of monetary value
        - Text quality indicators
        """
        if not text:
            return Decimal("0.00")

        score = Decimal("50.00")  # Base score

        # Bonus for finding a value
        if extracted_value:
            score += Decimal("30.00")

        # Bonus for longer text (more context)
        if len(text) > 50:
            score += Decimal("10.00")

        # Penalty for very short text
        if len(text) < 20:
            score -= Decimal("20.00")

        return min(max(score, Decimal("0.00")), Decimal("100.00"))

    @classmethod
    async def process_receipt(cls, image_path: str) -> Tuple[str, Optional[Decimal], Decimal]:
        """
        Process receipt image: extract text and value

        Returns:
            Tuple of (ocr_text, extracted_value, confidence_score)
        """
        # Extract text
        text = await cls.extract_text(image_path)

        # Extract value
        value = cls.extract_value(text)

        # Calculate confidence
        confidence = cls.calculate_confidence(text, value)

        logger.info(f"OCR processing complete: value={value}, confidence={confidence}")

        return text, value, confidence
```

## 5. Rota de Upload - `app/api/v1/receipts.py`

```python
"""
Receipts API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.security import get_current_user
from app.models.user import User
from app.models.receipt import ReceiptResponse, ReceiptUpdate
from app.services.ocr_service import OCRService
from app.services.storage_service import StorageService
from app.services.supabase_service import SupabaseService
from app.utils.image import validate_image, optimize_image

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post("", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def upload_receipt(
    report_id: str = Form(...),
    file: UploadFile = File(...),
    value: float | None = Form(None),
    date: str | None = Form(None),
    description: str | None = Form(None),
    notes: str | None = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a new receipt with OCR processing

    - **file**: Image file (JPEG, PNG, WebP)
    - **report_id**: ID of the report to attach receipt to
    - **value**: Optional manual value (if not provided, OCR will extract)
    - **date**: Optional date (defaults to today)
    - **description**: Optional description
    - **notes**: Optional notes
    """
    try:
        # Validate image
        await validate_image(file)

        # Save temporary file
        temp_path = f"uploads/temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Optimize image
        optimized_path = await optimize_image(temp_path)

        # Process OCR if value not provided
        ocr_text = None
        ocr_confidence = None
        extracted_value = value

        if value is None:
            ocr_text, extracted_value, ocr_confidence = await OCRService.process_receipt(
                optimized_path
            )

            if extracted_value is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Could not extract value from receipt. Please provide manually."
                )

        # Upload to Supabase Storage
        image_url = await StorageService.upload_receipt(
            file_path=optimized_path,
            user_id=current_user.id,
            report_id=report_id
        )

        # Save to database
        receipt_data = {
            "report_id": report_id,
            "user_id": current_user.id,
            "value": float(extracted_value),
            "date": date,
            "description": description,
            "notes": notes,
            "image_url": image_url,
            "ocr_text": ocr_text,
            "ocr_confidence": float(ocr_confidence) if ocr_confidence else None,
            "ocr_status": "processed" if ocr_text else "pending"
        }

        supabase = SupabaseService()
        receipt = await supabase.create_receipt(receipt_data)

        # Cleanup temp files
        import os
        os.remove(temp_path)
        if optimized_path != temp_path:
            os.remove(optimized_path)

        logger.info(f"Receipt created: {receipt['id']}")
        return receipt

    except Exception as e:
        logger.error(f"Error uploading receipt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific receipt"""
    supabase = SupabaseService()
    receipt = await supabase.get_receipt(receipt_id, current_user.id)

    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )

    return receipt


@router.put("/{receipt_id}", response_model=ReceiptResponse)
async def update_receipt(
    receipt_id: str,
    receipt_update: ReceiptUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a receipt"""
    supabase = SupabaseService()
    receipt = await supabase.update_receipt(
        receipt_id,
        current_user.id,
        receipt_update.dict(exclude_unset=True)
    )

    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )

    logger.info(f"Receipt updated: {receipt_id}")
    return receipt


@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_receipt(
    receipt_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a receipt"""
    supabase = SupabaseService()
    success = await supabase.delete_receipt(receipt_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Receipt not found"
        )

    logger.info(f"Receipt deleted: {receipt_id}")
    return None
```

## 6. Autenticação - `app/core/security.py`

```python
"""
Security utilities: JWT, password hashing, authentication
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.models.user import User
from app.services.supabase_service import SupabaseService

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Data to encode in token (typically {"sub": user_id})
        expires_delta: Token expiration time
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get current authenticated user

    Usage in routes:
        current_user: User = Depends(get_current_user)
    """
    token = credentials.credentials
    payload = decode_token(token)

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Get user from Supabase
    supabase = SupabaseService()
    user = await supabase.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return User(**user)
```

## 7. Testes - `tests/test_receipts.py`

```python
"""
Tests for receipts endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_headers(test_user_token):
    """Fixture to provide authentication headers"""
    return {"Authorization": f"Bearer {test_user_token}"}


def test_upload_receipt_success(auth_headers, test_report_id):
    """Test successful receipt upload with OCR"""
    with open("tests/fixtures/receipt.jpg", "rb") as f:
        response = client.post(
            "/api/v1/receipts",
            headers=auth_headers,
            data={"report_id": test_report_id},
            files={"file": ("receipt.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "value" in data
    assert data["ocr_status"] == "processed"


def test_upload_receipt_invalid_file(auth_headers, test_report_id):
    """Test upload with invalid file type"""
    response = client.post(
        "/api/v1/receipts",
        headers=auth_headers,
        data={"report_id": test_report_id},
        files={"file": ("test.txt", b"test", "text/plain")}
    )

    assert response.status_code == 422


def test_get_receipt(auth_headers, test_receipt_id):
    """Test get receipt by ID"""
    response = client.get(
        f"/api/v1/receipts/{test_receipt_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_receipt_id
```

## Próximos Passos

1. Implementar todos os endpoints (reports, auth, profile)
2. Adicionar serviço de geração de PDF
3. Configurar testes completos
4. Setup CI/CD
5. Deploy para Render.com

Veja `deployment.md` para instruções de deploy.
