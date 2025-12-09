"""
Application Dependencies Module

FastAPI dependency injection functions.
Provides common dependencies for routes and services.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import Optional
from uuid import UUID
from fastapi import Depends, Header, HTTPException, status
from supabase import Client
from loguru import logger

from app.repositories.supabase_client import get_supabase_client
from app.config import settings
from app.core.security.jwt import decode_access_token
from app.core.exceptions.auth import InvalidTokenException, TokenExpiredException, MissingTokenException


# ----------------------------------------
# Database Dependencies
# ----------------------------------------
def get_db() -> Client:
    """
    Get Supabase client dependency.

    Returns:
        Client: Supabase client instance

    Usage:
        @app.get("/items")
        async def get_items(db: Client = Depends(get_db)):
            response = db.table("items").select("*").execute()
            return response.data
    """
    return get_supabase_client()


# ----------------------------------------
# Authentication Dependencies
# ----------------------------------------
async def get_current_user_id(
    authorization: Optional[str] = Header(None),
    db: Client = Depends(get_db)
) -> str:
    """
    Extract and validate user ID from JWT token.

    Args:
        authorization: Authorization header with Bearer token
        db: Supabase client

    Returns:
        str: User ID (UUID)

    Raises:
        HTTPException: If token is invalid or missing

    Usage:
        @app.get("/me")
        async def get_me(user_id: str = Depends(get_current_user_id)):
            return {"user_id": user_id}

    Note:
        This is a placeholder. Full JWT validation will be implemented
        in app.core.security.dependencies module.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode and validate JWT token
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise InvalidTokenException(
                details={"error": "Missing user ID in token"}
            )

        # Validate UUID format
        try:
            UUID(user_id)
        except ValueError:
            raise InvalidTokenException(
                details={"error": "Invalid user ID format"}
            )

        logger.debug(f"Authenticated user: {user_id}")

        return user_id

    except TokenExpiredException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user_id(
    authorization: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Extract user ID from token if present (optional).

    Useful for endpoints that work for both authenticated and anonymous users.

    Args:
        authorization: Optional authorization header

    Returns:
        Optional[str]: User ID if authenticated, None otherwise

    Usage:
        @app.get("/items")
        async def get_items(user_id: Optional[str] = Depends(get_optional_user_id)):
            if user_id:
                # Return user-specific items
                pass
            else:
                # Return public items
                pass
    """
    if not authorization:
        return None

    try:
        return await get_current_user_id(authorization=authorization)
    except HTTPException:
        return None


# ----------------------------------------
# Pagination Dependencies
# ----------------------------------------
class Pagination:
    """
    Pagination parameters dependency.

    Provides limit and offset for paginated queries.
    """

    def __init__(
        self,
        limit: int = 20,
        offset: int = 0
    ):
        """
        Initialize pagination parameters.

        Args:
            limit: Maximum number of items (1-100, default: 20)
            offset: Number of items to skip (default: 0)

        Raises:
            HTTPException: If parameters are invalid
        """
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )

        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative"
            )

        self.limit = limit
        self.offset = offset

    def __repr__(self):
        return f"Pagination(limit={self.limit}, offset={self.offset})"


def get_pagination(
    limit: int = 20,
    offset: int = 0
) -> Pagination:
    """
    Get pagination parameters dependency.

    Args:
        limit: Maximum number of items (default: 20)
        offset: Number of items to skip (default: 0)

    Returns:
        Pagination: Pagination parameters

    Usage:
        @app.get("/items")
        async def get_items(pagination: Pagination = Depends(get_pagination)):
            items = await repo.find_all(
                limit=pagination.limit,
                offset=pagination.offset
            )
            return items
    """
    return Pagination(limit=limit, offset=offset)


# ----------------------------------------
# Header Dependencies
# ----------------------------------------
async def verify_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> bool:
    """
    Verify API key from header (optional security layer).

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        bool: True if valid

    Raises:
        HTTPException: If API key is invalid

    Usage:
        @app.get("/admin/stats")
        async def get_stats(_: bool = Depends(verify_api_key)):
            # Protected endpoint
            return {"stats": "..."}

    Note:
        This is a simple example. In production, use more secure methods
        like JWT tokens or OAuth2.
    """
    # TODO: Implement API key validation if needed
    # For now, this is a placeholder

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )

    # In production, validate against stored keys
    # For now, just check if it exists
    # valid_keys = settings.API_KEYS  # Add to config if needed

    return True


async def get_user_agent(
    user_agent: Optional[str] = Header(None, alias="User-Agent")
) -> Optional[str]:
    """
    Get User-Agent header.

    Useful for analytics and debugging.

    Args:
        user_agent: User-Agent header value

    Returns:
        Optional[str]: User agent string

    Usage:
        @app.post("/events")
        async def log_event(
            user_agent: Optional[str] = Depends(get_user_agent)
        ):
            logger.info(f"Event from: {user_agent}")
    """
    return user_agent


# ----------------------------------------
# Request ID Dependency
# ----------------------------------------
async def get_request_id(
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID")
) -> Optional[str]:
    """
    Get or generate request ID for tracing.

    Args:
        x_request_id: Request ID from header

    Returns:
        Optional[str]: Request ID

    Usage:
        @app.post("/items")
        async def create_item(
            request_id: Optional[str] = Depends(get_request_id)
        ):
            logger.info(f"[{request_id}] Creating item...")
    """
    return x_request_id
