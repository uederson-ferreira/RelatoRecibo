"""
Reports Endpoints Module

Handles report CRUD operations and management.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from loguru import logger

from app.dependencies import get_db, get_pagination, get_current_user_id, Pagination
from app.models.report.create import ReportCreate
from app.models.report.update import ReportUpdate
from app.models.report.response import ReportResponse, ReportSummary
from app.models.report.enums import ReportStatus
from app.models.base import PaginatedResponse, SuccessResponse
from app.repositories.report_repository import ReportRepository
from app.core.exceptions.report import (
    ReportNotFoundException,
    ReportAccessDeniedException
)


router = APIRouter()


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new report.

    - **name**: Report name (3-200 characters)
    - **description**: Optional description
    - **start_date**: Optional start date for report period
    - **end_date**: Optional end date (must be >= start_date)
    - **notes**: Optional notes

    Returns:
    - Created report with generated ID

    Raises:
    - 401: Unauthorized (missing or invalid token)
    - 422: Validation error
    """
    try:
        repo = ReportRepository(db)

        # Prepare report data
        report_dict = report_data.model_dump()
        report_dict["user_id"] = user_id
        report_dict["status"] = ReportStatus.DRAFT.value

        # Create report
        created = await repo.create(report_dict)

        logger.info(f"Report created: {created['id']}")

        return ReportResponse(**created)

    except Exception as e:
        logger.error(f"Error creating report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report"
        )


@router.get("", response_model=PaginatedResponse)
async def list_reports(
    status: ReportStatus = Query(None, description="Filter by status"),
    pagination: Pagination = Depends(get_pagination),
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    List all reports for authenticated user.

    Query Parameters:
    - **status**: Filter by status (draft, completed, archived)
    - **limit**: Items per page (default: 20, max: 100)
    - **offset**: Pagination offset (default: 0)

    Returns:
    - Paginated list of reports
    - Total count and pagination metadata

    Raises:
    - 401: Unauthorized (missing or invalid token)
    """
    try:
        repo = ReportRepository(db)

        # Fetch reports
        reports = await repo.find_by_user(
            user_id=UUID(user_id),
            status=status.value if status else None,
            limit=pagination.limit,
            offset=pagination.offset
        )

        # Count total
        total = await repo.count_by_user(
            user_id=UUID(user_id),
            status=status.value if status else None
        )

        # Convert to summary format
        items = [ReportSummary(**report) for report in reports]

        logger.info(f"Listed {len(items)} reports for user {user_id}")

        return PaginatedResponse(
            items=items,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset
        )

    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list reports"
        )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific report by ID.

    Path Parameters:
    - **report_id**: Report UUID

    Returns:
    - Report details

    Raises:
    - 401: Unauthorized (missing or invalid token)
    - 404: Report not found
    - 403: Access denied (not owner)
    """
    try:
        repo = ReportRepository(db)

        # Fetch report
        report = await repo.find_by_id_and_user(
            report_id=report_id,
            user_id=UUID(user_id)
        )

        if not report:
            raise ReportNotFoundException(
                details={"report_id": str(report_id)}
            )

        logger.info(f"Report retrieved: {report_id}")

        return ReportResponse(**report)

    except ReportNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get report"
        )


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: UUID,
    update_data: ReportUpdate,
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update a report.

    Path Parameters:
    - **report_id**: Report UUID

    Body (all optional):
    - **name**: New name
    - **description**: New description
    - **start_date**: New start date
    - **end_date**: New end date
    - **notes**: New notes
    - **status**: New status (draft, completed, archived)

    Returns:
    - Updated report

    Raises:
    - 401: Unauthorized (missing or invalid token)
    - 404: Report not found
    - 403: Access denied
    - 422: Validation error
    """
    try:
        repo = ReportRepository(db)

        # Check if report exists and user has access
        existing = await repo.find_by_id_and_user(
            report_id=report_id,
            user_id=UUID(user_id)
        )

        if not existing:
            raise ReportNotFoundException(
                details={"report_id": str(report_id)}
            )

        # Update report
        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            # No fields to update
            return ReportResponse(**existing)

        updated = await repo.update(report_id, update_dict)

        if not updated:
            raise ReportNotFoundException(
                details={"report_id": str(report_id)}
            )

        logger.info(f"Report updated: {report_id}")

        return ReportResponse(**updated)

    except ReportNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error updating report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update report"
        )


@router.delete("/{report_id}", response_model=SuccessResponse)
async def delete_report(
    report_id: UUID,
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a report.

    Path Parameters:
    - **report_id**: Report UUID

    Returns:
    - Success message

    Raises:
    - 401: Unauthorized (missing or invalid token)
    - 404: Report not found
    - 403: Access denied

    Note:
    - This will also delete all associated receipts (cascade)
    """
    try:
        repo = ReportRepository(db)

        # Check if report exists and user has access
        existing = await repo.find_by_id_and_user(
            report_id=report_id,
            user_id=UUID(user_id)
        )

        if not existing:
            raise ReportNotFoundException(
                details={"report_id": str(report_id)}
            )

        # Delete report
        deleted = await repo.delete(report_id)

        if not deleted:
            raise ReportNotFoundException(
                details={"report_id": str(report_id)}
            )

        logger.info(f"Report deleted: {report_id}")

        return SuccessResponse(
            success=True,
            message=f"Report {report_id} deleted successfully"
        )

    except ReportNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )
