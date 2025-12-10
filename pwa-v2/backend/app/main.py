"""
RelatoRecibo Backend API

FastAPI application entry point.
Main application configuration and setup.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.config import settings
from app.api.v1.router import api_router
from app.core.exceptions.base import AppException


# ----------------------------------------
# Configure logger
# ----------------------------------------
def setup_logger():
    """Configure loguru logger with file rotation."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Add file handler with rotation
    logger.add(
        settings.LOG_FILE,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        level=settings.LOG_LEVEL,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        backtrace=True,
        diagnose=True
    )

    logger.info(f"Logger initialized - Level: {settings.LOG_LEVEL}")


setup_logger()


# ----------------------------------------
# Create FastAPI application
# ----------------------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    # RelatoRecibo API v2.0

    API moderna para gest?o de recibos e presta??o de contas.

    ## Recursos principais:
    - =? Upload de fotos de recibos
    - =
 OCR autom?tico para detectar valores
    - =? Gera??o de PDF profissional
    - = Autentica??o JWT
    - =? Armazenamento seguro (Supabase)

    ## Stack tecnol?gica:
    - **Backend:** Python 3.11+ + FastAPI
    - **Database:** PostgreSQL (Supabase)
    - **Storage:** Supabase Storage
    - **OCR:** Tesseract
    - **PDF:** ReportLab
    """,
    version=settings.VERSION,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url="/api/openapi.json" if not settings.is_production else None,
    contact={
        "name": "RelatoRecibo Team",
        "email": "contact@relatorecibo.com"
    },
    license_info={
        "name": "MIT",
    }
)

logger.info(
    f"FastAPI app created - Environment: {settings.ENVIRONMENT}, "
    f"Version: {settings.VERSION}"
)


# ----------------------------------------
# CORS Middleware
# ----------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "X-Total-Count"]
)

logger.info(f"CORS configured for origins: {settings.allowed_origins_list}")


# ----------------------------------------
# Include API routers
# ----------------------------------------
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
logger.info(f"API v1 router included at {settings.API_V1_PREFIX}")


# ----------------------------------------
# Exception handlers
# ----------------------------------------
@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    """Handle custom application exceptions."""
    logger.error(f"AppException: {exc.code} - {exc.message}")
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


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.DEBUG else None
            }
        }
    )


# ----------------------------------------
# Application event handlers
# ----------------------------------------
@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup.

    - Initialize database connections
    - Setup scheduled tasks
    - Validate configuration
    """
    logger.info("=" * 50)
    logger.info(f"=? Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Docs URL: {settings.docs_url or 'Disabled'}")
    logger.info("=" * 50)

    # Validate Supabase connection
    try:
        from app.repositories.supabase_client import get_supabase_client
        client = get_supabase_client()
        logger.info(" Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"L Failed to initialize Supabase client: {e}")
        if settings.is_production:
            raise

    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f" Upload directory ready: {upload_dir.absolute()}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown.

    - Close database connections
    - Cleanup resources
    """
    logger.info("=" * 50)
    logger.info(f"=? Shutting down {settings.PROJECT_NAME}")
    logger.info("=" * 50)

    # Close Supabase client
    try:
        from app.repositories.supabase_client import SupabaseClient
        SupabaseClient.close()
        logger.info(" Supabase client closed")
    except Exception as e:
        logger.error(f"L Error closing Supabase client: {e}")


# ----------------------------------------
# Root endpoints
# ----------------------------------------
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.

    Returns basic API information and links to documentation.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": settings.docs_url or "Documentation disabled in production",
        "health": "/health",
        "api": settings.API_V1_PREFIX
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Used by monitoring tools and load balancers to verify service status.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


# ----------------------------------------
# Development server runner
# ----------------------------------------
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
