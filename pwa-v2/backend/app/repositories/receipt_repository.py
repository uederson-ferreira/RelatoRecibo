"""
Receipt Repository Module

Data access layer for receipts.
Handles all database operations for receipts table.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from loguru import logger

from app.repositories.base import BaseRepository


class ReceiptRepository(BaseRepository):
    """
    Repository for Receipt entity.

    Provides CRUD operations and custom queries for receipts.
    Uses Row Level Security (RLS) for user isolation.
    """

    TABLE_NAME = "receipts"

    async def find_by_report(
        self,
        report_id: UUID,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Find all receipts for a specific report.

        Args:
            report_id: Report UUID
            user_id: User UUID (for RLS validation)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of receipt records

        Example:
            >>> receipts = await repo.find_by_report(
            ...     report_id=uuid.uuid4(),
            ...     user_id=uuid.uuid4(),
            ...     limit=50
            ... )
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .select("*")
                .eq("report_id", str(report_id))
                .eq("user_id", str(user_id))
                .order("date", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            logger.info(
                f"Found {len(response.data)} receipts for report {report_id}"
            )
            return response.data

        except Exception as e:
            logger.error(
                f"Error finding receipts for report {report_id}: {e}"
            )
            raise

    async def find_by_id_and_user(
        self,
        receipt_id: UUID,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Find a receipt by ID for a specific user.

        Args:
            receipt_id: Receipt UUID
            user_id: User UUID

        Returns:
            Receipt record or None if not found

        Note:
            RLS ensures only the owner can access the receipt.

        Example:
            >>> receipt = await repo.find_by_id_and_user(
            ...     receipt_id=uuid.uuid4(),
            ...     user_id=uuid.uuid4()
            ... )
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .select("*")
                .eq("id", str(receipt_id))
                .eq("user_id", str(user_id))
                .maybe_single()
                .execute()
            )

            if response.data:
                logger.debug(
                    f"Receipt {receipt_id} found for user {user_id}"
                )
            else:
                logger.debug(
                    f"Receipt {receipt_id} not found for user {user_id}"
                )

            return response.data

        except Exception as e:
            logger.error(
                f"Error finding receipt {receipt_id} for user {user_id}: {e}"
            )
            raise

    async def find_by_status(
        self,
        user_id: UUID,
        status: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Find receipts by status for a user.

        Useful for finding pending/processing receipts for OCR.

        Args:
            user_id: User UUID
            status: Receipt status (pending, processing, processed, error)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of receipt records

        Example:
            >>> pending_receipts = await repo.find_by_status(
            ...     user_id=uuid.uuid4(),
            ...     status="pending",
            ...     limit=10
            ... )
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .select("*")
                .eq("user_id", str(user_id))
                .eq("status", status)
                .order("created_at", desc=False)  # Oldest first for processing
                .range(offset, offset + limit - 1)
                .execute()
            )

            logger.info(
                f"Found {len(response.data)} {status} receipts for user {user_id}"
            )
            return response.data

        except Exception as e:
            logger.error(
                f"Error finding {status} receipts for user {user_id}: {e}"
            )
            raise

    async def update_ocr_result(
        self,
        receipt_id: UUID,
        ocr_text: str,
        ocr_confidence: float,
        status: str = "processed"
    ) -> Optional[Dict[str, Any]]:
        """
        Update receipt with OCR processing results.

        Args:
            receipt_id: Receipt UUID
            ocr_text: Extracted text from OCR
            ocr_confidence: Confidence score (0-1)
            status: New status (default: "processed")

        Returns:
            Updated receipt or None if not found

        Example:
            >>> receipt = await repo.update_ocr_result(
            ...     receipt_id=uuid.uuid4(),
            ...     ocr_text="HOTEL IBIS\\nVALOR: R$ 125,50",
            ...     ocr_confidence=0.95
            ... )
        """
        try:
            update_data = {
                "ocr_text": ocr_text,
                "ocr_confidence": ocr_confidence,
                "status": status,
                "ocr_error": None  # Clear any previous error
            }

            updated = await self.update(receipt_id, update_data)

            if updated:
                logger.info(
                    f"OCR results updated for receipt {receipt_id}"
                )
            else:
                logger.warning(
                    f"Receipt {receipt_id} not found for OCR update"
                )

            return updated

        except Exception as e:
            logger.error(
                f"Error updating OCR results for receipt {receipt_id}: {e}"
            )
            raise

    async def update_ocr_error(
        self,
        receipt_id: UUID,
        error_message: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update receipt with OCR processing error.

        Args:
            receipt_id: Receipt UUID
            error_message: Error description

        Returns:
            Updated receipt or None if not found

        Example:
            >>> receipt = await repo.update_ocr_error(
            ...     receipt_id=uuid.uuid4(),
            ...     error_message="Low image quality"
            ... )
        """
        try:
            update_data = {
                "status": "error",
                "ocr_error": error_message
            }

            updated = await self.update(receipt_id, update_data)

            if updated:
                logger.info(
                    f"OCR error updated for receipt {receipt_id}"
                )

            return updated

        except Exception as e:
            logger.error(
                f"Error updating OCR error for receipt {receipt_id}: {e}"
            )
            raise

    async def count_by_report(
        self,
        report_id: UUID
    ) -> int:
        """
        Count receipts in a report.

        Args:
            report_id: Report UUID

        Returns:
            Total count of receipts

        Example:
            >>> count = await repo.count_by_report(uuid.uuid4())
        """
        return await self.count({"report_id": str(report_id)})
