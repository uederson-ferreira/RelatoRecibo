"""
Application Constants Module

Global constants used throughout the application.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

# ----------------------------------------
# File Upload Constants
# ----------------------------------------
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"]
MAX_UPLOAD_SIZE_MB = 5
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024

# Image dimensions
MAX_IMAGE_WIDTH = 4096
MAX_IMAGE_HEIGHT = 4096
THUMBNAIL_SIZE = (300, 300)

# ----------------------------------------
# Receipt Constants
# ----------------------------------------
RECEIPT_CATEGORIES = [
    "Hospedagem",
    "Transporte",
    "Alimentação",
    "Combustível",
    "Estacionamento",
    "Pedágio",
    "Material",
    "Serviços",
    "Outros"
]

# ----------------------------------------
# Report Constants
# ----------------------------------------
REPORT_STATUSES = ["draft", "completed", "archived"]

# ----------------------------------------
# OCR Constants
# ----------------------------------------
OCR_CONFIDENCE_THRESHOLD = 0.7  # 70% minimum confidence
OCR_TIMEOUT_SECONDS = 30
OCR_LANGUAGES = ["por", "eng"]  # Portuguese and English

# ----------------------------------------
# Pagination Constants
# ----------------------------------------
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1

# ----------------------------------------
# Currency Constants
# ----------------------------------------
CURRENCY_CODE = "BRL"
CURRENCY_SYMBOL = "R$"
DECIMAL_PLACES = 2

# ----------------------------------------
# Date Format Constants
# ----------------------------------------
DATE_FORMAT_BR = "%d/%m/%Y"
DATETIME_FORMAT_BR = "%d/%m/%Y %H:%M"
DATETIME_FORMAT_FULL = "%d/%m/%Y %H:%M:%S"
ISO_DATE_FORMAT = "%Y-%m-%d"
ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

# ----------------------------------------
# Validation Constants
# ----------------------------------------
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 100
MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000
MAX_NOTES_LENGTH = 2000

# ----------------------------------------
# Storage Constants
# ----------------------------------------
STORAGE_BUCKET_RECEIPTS = "receipts"
STORAGE_PATH_ORIGINALS = "originals"
STORAGE_PATH_THUMBNAILS = "thumbnails"
STORAGE_PATH_PDFS = "pdfs"

# ----------------------------------------
# API Constants
# ----------------------------------------
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Rate limiting
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW_SECONDS = 60

# ----------------------------------------
# Error Codes
# ----------------------------------------
ERROR_CODE_VALIDATION = "VALIDATION_ERROR"
ERROR_CODE_NOT_FOUND = "NOT_FOUND"
ERROR_CODE_UNAUTHORIZED = "UNAUTHORIZED"
ERROR_CODE_FORBIDDEN = "FORBIDDEN"
ERROR_CODE_CONFLICT = "CONFLICT"
ERROR_CODE_INTERNAL = "INTERNAL_SERVER_ERROR"
