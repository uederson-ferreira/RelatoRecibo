"""
Report Exception Module

Defines report-specific exceptions.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import Optional, Dict, Any

from app.core.exceptions.base import (
    NotFoundException,
    BadRequestException,
    ForbiddenException,
    ConflictException
)


class ReportNotFoundException(NotFoundException):
    """
    Raised when report is not found.

    Example:
        raise ReportNotFoundException(
            details={"report_id": "123e4567-e89b-12d3-a456-426614174000"}
        )
    """

    def __init__(
        self,
        message: str = "Report not found",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="REPORT_NOT_FOUND",
            details=details
        )


class ReportAccessDeniedException(ForbiddenException):
    """
    Raised when user tries to access report they don't own.

    Example:
        raise ReportAccessDeniedException(
            details={
                "report_id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51a2-43f7-8e6b-123456789abc"
            }
        )
    """

    def __init__(
        self,
        message: str = "You don't have access to this report",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="REPORT_ACCESS_DENIED",
            details=details
        )


class ReportAlreadyCompletedException(BadRequestException):
    """
    Raised when trying to modify a completed report.

    Example:
        raise ReportAlreadyCompletedException(
            details={"report_id": "123e4567-e89b-12d3-a456-426614174000"}
        )
    """

    def __init__(
        self,
        message: str = "Cannot modify completed report",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="REPORT_ALREADY_COMPLETED",
            details=details
        )


class ReportAlreadyArchivedException(BadRequestException):
    """
    Raised when trying to modify an archived report.

    Example:
        raise ReportAlreadyArchivedException(
            details={"report_id": "123e4567-e89b-12d3-a456-426614174000"}
        )
    """

    def __init__(
        self,
        message: str = "Cannot modify archived report",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="REPORT_ALREADY_ARCHIVED",
            details=details
        )


class InvalidReportStatusException(BadRequestException):
    """
    Raised when report status transition is invalid.

    Example:
        raise InvalidReportStatusException(
            message="Cannot change status from archived to draft",
            details={
                "current_status": "archived",
                "requested_status": "draft",
                "allowed_statuses": ["completed"]
            }
        )
    """

    def __init__(
        self,
        message: str = "Invalid report status transition",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="INVALID_REPORT_STATUS",
            details=details
        )


class EmptyReportException(BadRequestException):
    """
    Raised when trying to complete report without receipts.

    Example:
        raise EmptyReportException(
            details={"report_id": "123e4567-e89b-12d3-a456-426614174000"}
        )
    """

    def __init__(
        self,
        message: str = "Cannot complete report without receipts",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="EMPTY_REPORT",
            details=details
        )


class ReportNameTooLongException(BadRequestException):
    """
    Raised when report name exceeds maximum length.

    Example:
        raise ReportNameTooLongException(
            details={"max_length": 200, "provided_length": 250}
        )
    """

    def __init__(
        self,
        message: str = "Report name is too long",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="REPORT_NAME_TOO_LONG",
            details=details
        )


class DuplicateReportNameException(ConflictException):
    """
    Raised when report name already exists for user.

    Example:
        raise DuplicateReportNameException(
            details={"name": "Viagem São Paulo 2025"}
        )
    """

    def __init__(
        self,
        message: str = "Report name already exists",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            code="DUPLICATE_REPORT_NAME",
            details=details
        )
