"""
Base Exception Module

Defines base exception classes for the application.
All custom exceptions should inherit from AppException.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import Optional, Dict, Any


class AppException(Exception):
    """
    Base application exception.

    All custom exceptions should inherit from this class.
    Provides consistent error structure across the application.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code (uppercase snake_case)
        status_code: HTTP status code
        details: Optional additional error details

    Example:
        raise AppException(
            message="Resource not found",
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource_id": "123"}
        )
    """

    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize application exception.

        Args:
            message: Human-readable error message
            code: Error code (e.g., "RESOURCE_NOT_FOUND")
            status_code: HTTP status code (default: 500)
            details: Optional additional details
        """
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of exception."""
        return f"[{self.code}] {self.message}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"{self.__class__.__name__}("
            f"code='{self.code}', "
            f"message='{self.message}', "
            f"status_code={self.status_code})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary.

        Returns:
            Dict with error information

        Example:
            >>> exc = AppException("Error", "ERROR_CODE", 400)
            >>> exc.to_dict()
            {
                "code": "ERROR_CODE",
                "message": "Error",
                "details": {}
            }
        """
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


# ----------------------------------------
# Common HTTP Exceptions
# ----------------------------------------

class BadRequestException(AppException):
    """
    400 Bad Request exception.

    Used when the request is malformed or contains invalid data.
    """

    def __init__(
        self,
        message: str = "Bad request",
        code: str = "BAD_REQUEST",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=400,
            details=details
        )


class UnauthorizedException(AppException):
    """
    401 Unauthorized exception.

    Used when authentication is required but missing or invalid.
    """

    def __init__(
        self,
        message: str = "Unauthorized",
        code: str = "UNAUTHORIZED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=401,
            details=details
        )


class ForbiddenException(AppException):
    """
    403 Forbidden exception.

    Used when user is authenticated but doesn't have permission.
    """

    def __init__(
        self,
        message: str = "Forbidden",
        code: str = "FORBIDDEN",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=403,
            details=details
        )


class NotFoundException(AppException):
    """
    404 Not Found exception.

    Used when a requested resource doesn't exist.
    """

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=404,
            details=details
        )


class ConflictException(AppException):
    """
    409 Conflict exception.

    Used when there's a conflict with current state (e.g., duplicate resource).
    """

    def __init__(
        self,
        message: str = "Resource conflict",
        code: str = "CONFLICT",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=409,
            details=details
        )


class ValidationException(AppException):
    """
    422 Unprocessable Entity exception.

    Used when request data fails validation.
    """

    def __init__(
        self,
        message: str = "Validation error",
        code: str = "VALIDATION_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=422,
            details=details
        )


class TooManyRequestsException(AppException):
    """
    429 Too Many Requests exception.

    Used when rate limit is exceeded.
    """

    def __init__(
        self,
        message: str = "Too many requests",
        code: str = "RATE_LIMIT_EXCEEDED",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=429,
            details=details
        )


class InternalServerException(AppException):
    """
    500 Internal Server Error exception.

    Used for unexpected server errors.
    """

    def __init__(
        self,
        message: str = "Internal server error",
        code: str = "INTERNAL_SERVER_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=500,
            details=details
        )


class ServiceUnavailableException(AppException):
    """
    503 Service Unavailable exception.

    Used when external service is temporarily unavailable.
    """

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        code: str = "SERVICE_UNAVAILABLE",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code=code,
            status_code=503,
            details=details
        )
