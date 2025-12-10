"""
Report Calculator Module

Service for calculating report totals and statistics.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from decimal import Decimal
from typing import Dict, Any, List
from uuid import UUID
from loguru import logger

from app.repositories.receipt_repository import ReceiptRepository


class ReportCalculator:
    """
    Service for calculating report statistics and totals.

    Features:
    - Calculate total value from receipts
    - Calculate receipt count
    - Calculate average receipt value
    - Calculate progress towards target
    """

    def __init__(self, receipt_repo: ReceiptRepository):
        """
        Initialize calculator.

        Args:
            receipt_repo: Receipt repository instance
        """
        self.receipt_repo = receipt_repo

    async def calculate_totals(
        self,
        report_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Calculate totals for a report.

        Args:
            report_id: Report UUID
            user_id: User UUID

        Returns:
            Dict with calculated values:
            - total_value: Sum of all receipt values
            - receipt_count: Number of receipts
            - average_value: Average receipt value
            - min_value: Minimum receipt value
            - max_value: Maximum receipt value
        """
        try:
            # Fetch all receipts for the report
            receipts = await self.receipt_repo.find_by_report(
                report_id=report_id,
                user_id=user_id,
                limit=10000  # Get all receipts
            )

            if not receipts:
                return {
                    "total_value": Decimal("0.00"),
                    "receipt_count": 0,
                    "average_value": Decimal("0.00"),
                    "min_value": None,
                    "max_value": None
                }

            # Extract values
            values = [
                Decimal(str(receipt.get("value", 0)))
                for receipt in receipts
                if receipt.get("value") is not None
            ]

            if not values:
                return {
                    "total_value": Decimal("0.00"),
                    "receipt_count": len(receipts),
                    "average_value": Decimal("0.00"),
                    "min_value": None,
                    "max_value": None
                }

            # Calculate statistics
            total_value = sum(values)
            receipt_count = len(receipts)
            average_value = total_value / receipt_count if receipt_count > 0 else Decimal("0.00")
            min_value = min(values)
            max_value = max(values)

            logger.info(
                f"Calculated totals for report {report_id}: "
                f"total={total_value}, count={receipt_count}"
            )

            return {
                "total_value": total_value,
                "receipt_count": receipt_count,
                "average_value": average_value,
                "min_value": min_value,
                "max_value": max_value
            }

        except Exception as e:
            logger.error(f"Error calculating totals for report {report_id}: {e}")
            raise

    async def calculate_progress(
        self,
        report_id: UUID,
        user_id: UUID,
        target_value: Decimal
    ) -> Dict[str, Any]:
        """
        Calculate progress towards target value.

        Args:
            report_id: Report UUID
            user_id: User UUID
            target_value: Target value to reach

        Returns:
            Dict with progress information:
            - current_value: Current total value
            - target_value: Target value
            - percentage: Progress percentage (0-100)
            - remaining: Remaining amount to reach target
            - exceeded: Whether target was exceeded
        """
        try:
            totals = await self.calculate_totals(report_id, user_id)
            current_value = totals["total_value"]

            if target_value <= 0:
                percentage = Decimal("0.00")
            else:
                percentage = (current_value / target_value) * 100

            remaining = target_value - current_value
            exceeded = current_value > target_value

            return {
                "current_value": current_value,
                "target_value": target_value,
                "percentage": percentage,
                "remaining": abs(remaining) if not exceeded else Decimal("0.00"),
                "exceeded": exceeded
            }

        except Exception as e:
            logger.error(f"Error calculating progress for report {report_id}: {e}")
            raise

    async def update_report_totals(
        self,
        report_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Calculate and return totals for updating a report.

        This is a convenience method that returns only the fields
        needed to update the report table.

        Args:
            report_id: Report UUID
            user_id: User UUID

        Returns:
            Dict with total_value and receipt_count
        """
        totals = await self.calculate_totals(report_id, user_id)

        return {
            "total_value": totals["total_value"],
            "receipt_count": totals["receipt_count"]
        }
