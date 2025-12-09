"""
JWT Security Module

Handles JWT token creation and validation.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from uuid import UUID
from jose import JWTError, jwt
from loguru import logger

from app.config import settings
from app.core.exceptions.auth import InvalidTokenException, TokenExpiredException


def create_access_token(
    user_id: UUID,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User UUID
        email: User email
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token(
        ...     user_id=uuid.uuid4(),
        ...     email="user@example.com"
        ... )
        >>> print(token)
        eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

    Note:
        Default expiration: 24 hours (from settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        Token includes: sub (user_id), email, iat, exp
    """
    try:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        # Token payload
        to_encode = {
            "sub": str(user_id),  # Subject (user ID)
            "email": email,
            "iat": datetime.utcnow(),  # Issued at
            "exp": expire,  # Expiration
            "type": "access"  # Token type
        }

        # Encode token
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

        logger.debug(f"Access token created for user {user_id}")
        return encoded_jwt

    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Dict with token payload (sub, email, exp, etc.)

    Raises:
        InvalidTokenException: If token is invalid or malformed
        TokenExpiredException: If token has expired

    Example:
        >>> payload = decode_access_token(token)
        >>> user_id = payload["sub"]
        >>> email = payload["email"]

    Note:
        Validates:
        - Signature (using JWT_SECRET_KEY)
        - Expiration time
        - Algorithm (HS256)
    """
    try:
        # Decode and validate token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Validate token type
        if payload.get("type") != "access":
            logger.warning("Invalid token type")
            raise InvalidTokenException(
                message="Invalid token type",
                details={"expected": "access", "got": payload.get("type")}
            )

        logger.debug(f"Token decoded successfully for user {payload.get('sub')}")
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise TokenExpiredException()

    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        raise InvalidTokenException(
            message="Could not validate token",
            details={"error": str(e)}
        )

    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        raise InvalidTokenException(
            message="Token validation failed",
            details={"error": str(e)}
        )


def get_user_id_from_token(token: str) -> str:
    """
    Extract user ID from JWT token.

    Convenience function to get user ID without needing full payload.

    Args:
        token: JWT token string

    Returns:
        User ID (UUID string)

    Raises:
        InvalidTokenException: If token is invalid
        TokenExpiredException: If token has expired

    Example:
        >>> user_id = get_user_id_from_token(token)
        >>> print(user_id)
        123e4567-e89b-12d3-a456-426614174000
    """
    payload = decode_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise InvalidTokenException(
            message="Token missing user ID",
            details={"field": "sub"}
        )

    return user_id


def get_email_from_token(token: str) -> str:
    """
    Extract email from JWT token.

    Args:
        token: JWT token string

    Returns:
        User email string

    Raises:
        InvalidTokenException: If token is invalid or missing email
        TokenExpiredException: If token has expired

    Example:
        >>> email = get_email_from_token(token)
        >>> print(email)
        user@example.com
    """
    payload = decode_access_token(token)
    email = payload.get("email")

    if not email:
        raise InvalidTokenException(
            message="Token missing email",
            details={"field": "email"}
        )

    return email


def verify_token(token: str) -> bool:
    """
    Verify if token is valid without raising exceptions.

    Useful for optional authentication checks.

    Args:
        token: JWT token string

    Returns:
        True if valid, False otherwise

    Example:
        >>> if verify_token(token):
        ...     # Token is valid
        ...     pass
        ... else:
        ...     # Token is invalid or expired
        ...     pass
    """
    try:
        decode_access_token(token)
        return True
    except (InvalidTokenException, TokenExpiredException):
        return False
