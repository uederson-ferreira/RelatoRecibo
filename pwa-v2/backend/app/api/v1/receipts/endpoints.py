"""
Receipts Endpoints Module

Handles receipt CRUD operations and file uploads.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from loguru import logger

from app.dependencies import get_db, get_pagination, Pagination
from app.models.receipt.create import ReceiptCreate
from app.models.receipt.update import ReceiptUpdate
from app.models.receipt.response import ReceiptResponse, ReceiptSummary
from app.models.receipt.enums import ReceiptStatus
from app.models.base import PaginatedResponse, SuccessResponse
from app.repositories.receipt_repository import ReceiptRepository
from app.repositories.report_repository import ReportRepository
from app.core.exceptions.receipt import ReceiptNotFoundException
from app.core.exceptions.report import ReportNotFoundException


router = APIRouter()


# TODO: Replace with actual user authentication
MOCK_USER_ID = "00000000-0000-0000-0000-000000000001"


@router.post("", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def create_receipt(
    receipt_data: ReceiptCreate,
    db: Client = Depends(get_db)
):
    """
    Create a new receipt.

    - **report_id**: UUID of the parent report
    - **value**: Receipt value (BRL, must be > 0)
    - **date**: Receipt date (cannot be in future)
    - **description**: Optional description
    - **category**: Optional category (e.g., "Hospedagem", "Transporte")
    - **notes**: Optional notes

    Returns:
    - Created receipt with generated ID

    Raises:
    - 404: Report not found
    - 422: Validation error
    """
    try:
        receipt_repo = ReceiptRepository(db)
        report_repo = ReportRepository(db)

        # TODO: Get user_id from JWT token
        user_id = MOCK_USER_ID

        # Verify report exists and user has access
        report = await report_repo.find_by_id_and_user(
            report_id=UUID(receipt_data.report_id),
            user_id=UUID(user_id)
        )

        if not report:
            raise ReportNotFoundException(
                details={"report_id": receipt_data.report_id}
            )

        # Prepare receipt data
        receipt_dict = receipt_data.model_dump()
        receipt_dict["user_id"] = user_id
        receipt_dict["status"] = ReceiptStatus.PENDING.value

        # Create receipt
        created = await receipt_repo.create(receipt_dict)

        logger.info(f"Receipt created: {created['id']}")

        return ReceiptResponse(**created)

    except ReportNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error creating receipt: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create receipt"
        )


@router.get("", response_model=PaginatedResponse)
async def list_receipts(
    report_id: UUID = Query(..., description="Filter by report ID"),
    pagination: Pagination = Depends(get_pagination),
    db: Client = Depends(get_db)
):
    """
    List all receipts for a specific report.

    Query Parameters:
    - **report_id**: Report UUID (required)
    - **limit**: Items per page (default: 20, max: 100)
    - **offset**: Pagination offset (default: 0)

    Returns:
    - Paginated list of receipts
    - Total count and pagination metadata

    Raises:
    - 404: Report not found
    """
    try:
        receipt_repo = ReceiptRepository(db)
        report_repo = ReportRepository(db)

        # TODO: Get user_id from JWT token
        user_id = MOCK_USER_ID

        # Verify report exists and user has access
        report = await report_repo.find_by_id_and_user(
            report_id=report_id,
            user_id=UUID(user_id)
        )

        if not report:
            raise ReportNotFoundException(
                details={"report_id": str(report_id)}
            )

        # Fetch receipts
        receipts = await receipt_repo.find_by_report(
            report_id=report_id,
            user_id=UUID(user_id),
            limit=pagination.limit,
            offset=pagination.offset
        )

        # Count total
        total = await receipt_repo.count_by_report(report_id)

        # Convert to summary format
        items = [ReceiptSummary(**receipt) for receipt in receipts]

        logger.info(f"Listed {len(items)} receipts for report {report_id}")

        return PaginatedResponse(
            items=items,
            total=total,
            limit=pagination.limit,
            offset=pagination.offset
        )

    except ReportNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error listing receipts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list receipts"
        )


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: UUID,
    db: Client = Depends(get_db)
):
    """
    Get a specific receipt by ID.

    Path Parameters:
    - **receipt_id**: Receipt UUID

    Returns:
    - Receipt details including OCR data and image URLs

    Raises:
    - 404: Receipt not found
    - 403: Access denied (not owner)
    """
    try:
        receipt_repo = ReceiptRepository(db)

        # TODO: Get user_id from JWT token
        user_id = MOCK_USER_ID

        # Fetch receipt
        receipt = await receipt_repo.find_by_id_and_user(
            receipt_id=receipt_id,
            user_id=UUID(user_id)
        )

        if not receipt:
            raise ReceiptNotFoundException(
                details={"receipt_id": str(receipt_id)}
            )

        logger.info(f"Receipt retrieved: {receipt_id}")

        return ReceiptResponse(**receipt)

    except ReceiptNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error getting receipt {receipt_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get receipt"
        )


@router.put("/{receipt_id}", response_model=ReceiptResponse)
async def update_receipt(
    receipt_id: UUID,
    update_data: ReceiptUpdate,
    db: Client = Depends(get_db)
):
    """
    Update a receipt.

    Path Parameters:
    - **receipt_id**: Receipt UUID

    Body (all optional):
    - **value**: New value
    - **date**: New date
    - **description**: New description
    - **category**: New category
    - **notes**: New notes

    Returns:
    - Updated receipt

    Raises:
    - 404: Receipt not found
    - 403: Access denied
    - 422: Validation error
    """
    try:
        receipt_repo = ReceiptRepository(db)

        # TODO: Get user_id from JWT token
        user_id = MOCK_USER_ID

        # Check if receipt exists and user has access
        existing = await receipt_repo.find_by_id_and_user(
            receipt_id=receipt_id,
            user_id=UUID(user_id)
        )

        if not existing:
            raise ReceiptNotFoundException(
                details={"receipt_id": str(receipt_id)}
            )

        # Update receipt
        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            # No fields to update
            return ReceiptResponse(**existing)

        updated = await receipt_repo.update(receipt_id, update_dict)

        if not updated:
            raise ReceiptNotFoundException(
                details={"receipt_id": str(receipt_id)}
            )

        logger.info(f"Receipt updated: {receipt_id}")

        return ReceiptResponse(**updated)

    except ReceiptNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error updating receipt {receipt_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update receipt"
        )


@router.delete("/{receipt_id}", response_model=SuccessResponse)
async def delete_receipt(
    receipt_id: UUID,
    db: Client = Depends(get_db)
):
    """
    Delete a receipt.

    Path Parameters:
    - **receipt_id**: Receipt UUID

    Returns:
    - Success message

    Raises:
    - 404: Receipt not found
    - 403: Access denied

    Note:
    - This will also delete associated images from storage
    - Report totals will be recalculated automatically
    """
    try:
        receipt_repo = ReceiptRepository(db)

        # TODO: Get user_id from JWT token
        user_id = MOCK_USER_ID

        # Check if receipt exists and user has access
        existing = await receipt_repo.find_by_id_and_user(
            receipt_id=receipt_id,
            user_id=UUID(user_id)
        )

        if not existing:
            raise ReceiptNotFoundException(
                details={"receipt_id": str(receipt_id)}
            )

        # Delete receipt
        deleted = await receipt_repo.delete(receipt_id)

        if not deleted:
            raise ReceiptNotFoundException(
                details={"receipt_id": str(receipt_id)}
            )

        logger.info(f"Receipt deleted: {receipt_id}")

        return SuccessResponse(
            success=True,
            message=f"Receipt {receipt_id} deleted successfully"
        )

    except ReceiptNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error deleting receipt {receipt_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete receipt"
        )
