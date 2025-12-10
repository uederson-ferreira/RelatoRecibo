"""
Receipts Endpoints Module

Handles receipt CRUD operations and file uploads.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, BackgroundTasks
from supabase import Client
from loguru import logger

from app.dependencies import get_db, get_pagination, get_current_user_id, Pagination
from app.models.receipt.create import ReceiptCreate
from app.models.receipt.update import ReceiptUpdate
from app.models.receipt.response import ReceiptResponse, ReceiptSummary
from app.models.receipt.enums import ReceiptStatus
from app.models.base import PaginatedResponse, SuccessResponse
from app.repositories.receipt_repository import ReceiptRepository
from app.repositories.report_repository import ReportRepository
from app.core.exceptions.receipt import ReceiptNotFoundException
from app.core.exceptions.report import ReportNotFoundException
from app.services.storage.uploader import StorageUploader
from app.services.ocr.extractor import OCRExtractor
from app.utils.validators.file import validate_image_file, validate_file_size
from app.utils.image.validator import validate_image_content, validate_image_dimensions


router = APIRouter()


def map_receipt_fields(receipt_data: dict) -> dict:
    """
    Map database field names and types to model field names/types.
    
    Converts Decimal values to strings for Supabase compatibility.
    """
    from decimal import Decimal
    
    mapped = dict(receipt_data)
    
    # Convert Decimal to string for Supabase
    if "value" in mapped:
        if isinstance(mapped["value"], Decimal):
            mapped["value"] = str(mapped["value"])
        elif isinstance(mapped["value"], (int, float)):
            mapped["value"] = str(mapped["value"])
    
    # Convert date to string if needed
    if "date" in mapped and hasattr(mapped["date"], "isoformat"):
        mapped["date"] = mapped["date"].isoformat()
    
    # Ensure UUIDs are strings
    for field in ["id", "report_id", "user_id"]:
        if field in mapped and mapped[field] is not None:
            mapped[field] = str(mapped[field])
    
    return mapped


async def process_ocr_background(
    receipt_id: UUID,
    image_data: bytes,
    db: Client
):
    """
    Background task to process OCR on receipt image.

    Args:
        receipt_id: Receipt UUID
        image_data: Image binary data
        db: Database client
    """
    try:
        logger.info(f"Starting OCR processing for receipt {receipt_id}")

        receipt_repo = ReceiptRepository(db)
        ocr_extractor = OCRExtractor()

        # Extract OCR data
        ocr_result = await ocr_extractor.extract_receipt_data(image_data)

        # Update receipt with OCR results
        update_data = {
            "ocr_text": ocr_result["text"],
            "ocr_confidence": float(ocr_result["confidence"]),
            "status": ReceiptStatus.PROCESSED.value
        }

        # If value was extracted and receipt doesn't have a value, update it
        if ocr_result["value"] and ocr_result["confidence"] >= 0.7:
            existing = await receipt_repo.find_by_id(receipt_id)
            if existing and not existing.get("value"):
                update_data["value"] = float(ocr_result["value"])
                logger.info(f"Auto-filled value: {ocr_result['value']}")

        await receipt_repo.update(receipt_id, update_data)

        logger.info(f"OCR processing completed for receipt {receipt_id}")

    except Exception as e:
        logger.error(f"OCR processing failed for receipt {receipt_id}: {e}")

        # Update receipt with error status
        try:
            await receipt_repo.update(receipt_id, {
                "status": ReceiptStatus.ERROR.value,
                "ocr_error": str(e)
            })
        except:
            pass


@router.post("", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def create_receipt(
    receipt_data: ReceiptCreate,
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
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
    - 401: Unauthorized (missing or invalid token)
    - 404: Report not found
    - 422: Validation error
    """
    try:
        receipt_repo = ReceiptRepository(db)
        report_repo = ReportRepository(db)

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
        receipt_dict["user_id"] = str(user_id)  # Convert to string for Supabase
        receipt_dict["status"] = ReceiptStatus.PENDING.value
        
        # Convert Decimal to string for Supabase (it expects string for DECIMAL columns)
        from decimal import Decimal
        if "value" in receipt_dict:
            if isinstance(receipt_dict["value"], Decimal):
                receipt_dict["value"] = str(receipt_dict["value"])
            elif isinstance(receipt_dict["value"], (int, float)):
                receipt_dict["value"] = str(receipt_dict["value"])
        
        # Ensure report_id is string
        if "report_id" in receipt_dict:
            receipt_dict["report_id"] = str(receipt_dict["report_id"])
        
        # Convert date to string if needed
        if "date" in receipt_dict and hasattr(receipt_dict["date"], "isoformat"):
            receipt_dict["date"] = receipt_dict["date"].isoformat()

        # Create receipt
        created = await receipt_repo.create(receipt_dict)

        logger.info(f"Receipt created: {created.get('id')}")

        return ReceiptResponse(**map_receipt_fields(created))

    except ReportNotFoundException:
        raise
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error("Error creating receipt", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create receipt: {error_msg}"
        )


@router.get("", response_model=PaginatedResponse)
async def list_receipts(
    report_id: UUID = Query(..., description="Filter by report ID"),
    pagination: Pagination = Depends(get_pagination),
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
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
    - 401: Unauthorized (missing or invalid token)
    - 404: Report not found
    """
    try:
        receipt_repo = ReceiptRepository(db)
        report_repo = ReportRepository(db)

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
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific receipt by ID.

    Path Parameters:
    - **receipt_id**: Receipt UUID

    Returns:
    - Receipt details including OCR data and image URLs

    Raises:
    - 401: Unauthorized (missing or invalid token)
    - 404: Receipt not found
    - 403: Access denied (not owner)
    """
    try:
        receipt_repo = ReceiptRepository(db)

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

        return ReceiptResponse(**map_receipt_fields(receipt))

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
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
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
    - 401: Unauthorized (missing or invalid token)
    - 404: Receipt not found
    - 403: Access denied
    - 422: Validation error
    """
    try:
        receipt_repo = ReceiptRepository(db)

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
        
        # Convert Decimal to string for Supabase
        from decimal import Decimal
        if "value" in update_dict:
            if isinstance(update_dict["value"], Decimal):
                update_dict["value"] = str(update_dict["value"])
            elif isinstance(update_dict["value"], (int, float)):
                update_dict["value"] = str(update_dict["value"])
        
        # Convert date to string if needed
        if "date" in update_dict and hasattr(update_dict["date"], "isoformat"):
            update_dict["date"] = update_dict["date"].isoformat()

        if not update_dict:
            # No fields to update
            return ReceiptResponse(**map_receipt_fields(existing))

        updated = await receipt_repo.update(receipt_id, update_dict)

        if not updated:
            raise ReceiptNotFoundException(
                details={"receipt_id": str(receipt_id)}
            )

        logger.info(f"Receipt updated: {receipt_id}")

        return ReceiptResponse(**map_receipt_fields(updated))

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
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a receipt.

    Path Parameters:
    - **receipt_id**: Receipt UUID

    Returns:
    - Success message

    Raises:
    - 401: Unauthorized (missing or invalid token)
    - 404: Receipt not found
    - 403: Access denied

    Note:
    - This will also delete associated images from storage
    - Report totals will be recalculated automatically
    """
    try:
        receipt_repo = ReceiptRepository(db)

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


@router.post("/{receipt_id}/upload", response_model=ReceiptResponse)
async def upload_receipt_image(
    receipt_id: UUID,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Client = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """
    Upload image for a receipt.

    Path Parameters:
    - **receipt_id**: Receipt UUID

    Form Data:
    - **file**: Image file (JPG, PNG, WEBP, max 5MB)

    Returns:
    - Updated receipt with image URLs and status changed to "processing"

    Raises:
    - 401: Unauthorized (missing or invalid token)
    - 404: Receipt not found
    - 403: Access denied
    - 400: Invalid file type or size
    - 422: Invalid image (corrupted, wrong dimensions)

    Note:
    - Image will be uploaded to Supabase Storage
    - Thumbnail will be generated automatically
    - OCR processing will start asynchronously
    - Receipt status will change to "processing"
    """
    try:
        receipt_repo = ReceiptRepository(db)

        # Check if receipt exists and user has access
        existing = await receipt_repo.find_by_id_and_user(
            receipt_id=receipt_id,
            user_id=UUID(user_id)
        )

        if not existing:
            raise ReceiptNotFoundException(
                details={"receipt_id": str(receipt_id)}
            )

        # Validate file metadata
        validate_image_file(file)

        # Read file content
        image_data = await file.read()

        # Validate file size
        validate_file_size(image_data)

        # Validate image content
        image = validate_image_content(image_data)
        validate_image_dimensions(image)

        # Upload to storage
        storage = StorageUploader(db)
        original_url, thumbnail_url = await storage.upload_image(
            image_data=image_data,
            user_id=UUID(user_id),
            receipt_id=receipt_id,
            content_type=file.content_type
        )

        # Update receipt with image URLs and change status to processing
        update_data = {
            "image_url": original_url,
            "thumbnail_url": thumbnail_url,
            "status": ReceiptStatus.PROCESSING.value
        }

        updated = await receipt_repo.update(receipt_id, update_data)

        if not updated:
            raise ReceiptNotFoundException(
                details={"receipt_id": str(receipt_id)}
            )

        logger.info(f"Image uploaded for receipt: {receipt_id}")

        # Trigger OCR processing in background
        background_tasks.add_task(
            process_ocr_background,
            receipt_id=receipt_id,
            image_data=image_data,
            db=db
        )

        return ReceiptResponse(**map_receipt_fields(updated))

    except ReceiptNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image for receipt {receipt_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )
