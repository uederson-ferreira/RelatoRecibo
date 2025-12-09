"""
Authentication Exception Module

Defines authentication and authorization specific exceptions.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import Optional, Dict, Any

from app.core.exceptions.base import (
    UnauthorizedException,
    ForbiddenException,
    BadRequestException
)


class InvalidCredentialsException(UnauthorizedException):
    """
    Raised when login credentials are invalid.

    Example:
        raise InvalidCredentialsException(
            details={"email": "user@example.com"}
        )
    """

    def __init__(
        self,
        message: str = "Invalid email or password",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="INVALID_CREDENTIALS",
            details=details
        )


class InvalidTokenException(UnauthorizedException):
    """
    Raised when JWT token is invalid or expired.

    Example:
        raise InvalidTokenException(
            message="Token has expired",
            details={"token_expired_at": "2025-12-09T12:00:00Z"}
        )
    """

    def __init__(
        self,
        message: str = "Invalid or expired token",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="INVALID_TOKEN",
            details=details
        )


class TokenExpiredException(UnauthorizedException):
    """
    Raised when JWT token has expired.

    Example:
        raise TokenExpiredException()
    """

    def __init__(
        self,
        message: str = "Token has expired",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="TOKEN_EXPIRED",
            details=details
        )


class MissingTokenException(UnauthorizedException):
    """
    Raised when authorization token is missing.

    Example:
        raise MissingTokenException()
    """

    def __init__(
        self,
        message: str = "Authorization token is required",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="MISSING_TOKEN",
            details=details
        )


class UserAlreadyExistsException(BadRequestException):
    """
    Raised when trying to create a user that already exists.

    Example:
        raise UserAlreadyExistsException(
            details={"email": "user@example.com"}
        )
    """

    def __init__(
        self,
        message: str = "User already exists",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="USER_ALREADY_EXISTS",
            details=details
        )


class UserNotFoundException(UnauthorizedException):
    """
    Raised when user is not found during authentication.

    Example:
        raise UserNotFoundException(
            details={"user_id": "123e4567-e89b-12d3-a456-426614174000"}
        )
    """

    def __init__(
        self,
        message: str = "User not found",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="USER_NOT_FOUND",
            details=details
        )


class InsufficientPermissionsException(ForbiddenException):
    """
    Raised when user doesn't have required permissions.

    Example:
        raise InsufficientPermissionsException(
            message="Admin access required",
            details={"required_role": "admin", "user_role": "user"}
        )
    """

    def __init__(
        self,
        message: str = "Insufficient permissions",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="INSUFFICIENT_PERMISSIONS",
            details=details
        )


class AccountDisabledException(ForbiddenException):
    """
    Raised when user account is disabled.

    Example:
        raise AccountDisabledException(
            details={"user_id": "123e4567-e89b-12d3-a456-426614174000"}
        )
    """

    def __init__(
        self,
        message: str = "Account is disabled",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="ACCOUNT_DISABLED",
            details=details
        )


class EmailNotVerifiedException(ForbiddenException):
    """
    Raised when user email is not verified.

    Example:
        raise EmailNotVerifiedException(
            details={"email": "user@example.com"}
        )
    """

    def __init__(
        self,
        message: str = "Email not verified",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="EMAIL_NOT_VERIFIED",
            details=details
        )


class WeakPasswordException(BadRequestException):
    """
    Raised when password doesn't meet security requirements.

    Example:
        raise WeakPasswordException(
            details={
                "min_length": 8,
                "requires_uppercase": True,
                "requires_number": True
            }
        )
    """

    def __init__(
        self,
        message: str = "Password does not meet security requirements",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="WEAK_PASSWORD",
            details=details
        )
