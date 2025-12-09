"""
Password Security Module

Handles password hashing and verification using bcrypt.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from passlib.context import CryptContext
from loguru import logger


# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Cost factor (higher = more secure but slower)
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string

    Example:
        >>> hashed = hash_password("MySecurePass123!")
        >>> print(hashed)
        $2b$12$...

    Note:
        Uses bcrypt with 12 rounds (cost factor).
        Hashing is intentionally slow to prevent brute force attacks.
    """
    try:
        hashed = pwd_context.hash(password)
        logger.debug("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Previously hashed password

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password("MySecurePass123!")
        >>> verify_password("MySecurePass123!", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False

    Note:
        This operation is intentionally slow (bcrypt design).
        Protects against timing attacks.
    """
    try:
        is_valid = pwd_context.verify(plain_password, hashed_password)

        if is_valid:
            logger.debug("Password verification successful")
        else:
            logger.debug("Password verification failed")

        return is_valid

    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if password hash needs to be updated.

    Useful when changing bcrypt rounds or upgrading hash algorithm.

    Args:
        hashed_password: Existing hashed password

    Returns:
        True if hash needs update, False otherwise

    Example:
        >>> if needs_rehash(user.password_hash):
        ...     new_hash = hash_password(plain_password)
        ...     # Update user password hash in database
    """
    try:
        return pwd_context.needs_update(hashed_password)
    except Exception as e:
        logger.error(f"Error checking password rehash: {e}")
        return False
