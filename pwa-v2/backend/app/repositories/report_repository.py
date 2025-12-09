"""
Report Repository Module

Data access layer for reports.
Handles all database operations for reports table.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from loguru import logger

from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository):
    """
    Repository for Report entity.

    Provides CRUD operations and custom queries for reports.
    Uses Row Level Security (RLS) for user isolation.
    """

    TABLE_NAME = "reports"

    async def find_by_user(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Find all reports for a specific user.

        Args:
            user_id: User UUID
            status: Optional status filter (draft, completed, archived)
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of report records

        Example:
            >>> reports = await repo.find_by_user(
            ...     user_id=uuid.uuid4(),
            ...     status="draft",
            ...     limit=10
            ... )
        """
        try:
            query = (
                self.client
                .table(self.TABLE_NAME)
                .select("*")
                .eq("user_id", str(user_id))
                .order("created_at", desc=True)
                .range(offset, offset + limit - 1)
            )

            # Apply status filter if provided
            if status:
                query = query.eq("status", status)

            response = query.execute()

            logger.info(
                f"Found {len(response.data)} reports for user {user_id}"
            )
            return response.data

        except Exception as e:
            logger.error(f"Error finding reports for user {user_id}: {e}")
            raise

    async def find_by_id_and_user(
        self,
        report_id: UUID,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Find a report by ID for a specific user.

        Args:
            report_id: Report UUID
            user_id: User UUID

        Returns:
            Report record or None if not found

        Note:
            RLS ensures only the owner can access the report.

        Example:
            >>> report = await repo.find_by_id_and_user(
            ...     report_id=uuid.uuid4(),
            ...     user_id=uuid.uuid4()
            ... )
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .select("*")
                .eq("id", str(report_id))
                .eq("user_id", str(user_id))
                .maybe_single()
                .execute()
            )

            if response.data:
                logger.debug(
                    f"Report {report_id} found for user {user_id}"
                )
            else:
                logger.debug(
                    f"Report {report_id} not found for user {user_id}"
                )

            return response.data

        except Exception as e:
            logger.error(
                f"Error finding report {report_id} for user {user_id}: {e}"
            )
            raise

    async def update_totals(
        self,
        report_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Recalculate and update report totals.

        This triggers the database function that recalculates:
        - total_value (sum of all receipts)
        - receipt_count

        Args:
            report_id: Report UUID

        Returns:
            Updated report or None if not found

        Note:
            This is automatically triggered by database triggers when
            receipts are added/updated/deleted. Use this for manual refresh.

        Example:
            >>> report = await repo.update_totals(uuid.uuid4())
        """
        try:
            # Call database function to recalculate totals
            response = (
                self.client
                .rpc(
                    "recalculate_report_totals",
                    {"p_report_id": str(report_id)}
                )
                .execute()
            )

            logger.info(f"Totals recalculated for report {report_id}")

            # Fetch updated report
            return await self.find_by_id(report_id)

        except Exception as e:
            logger.error(
                f"Error updating totals for report {report_id}: {e}"
            )
            raise

    async def count_by_user(
        self,
        user_id: UUID,
        status: Optional[str] = None
    ) -> int:
        """
        Count reports for a user.

        Args:
            user_id: User UUID
            status: Optional status filter

        Returns:
            Total count of reports

        Example:
            >>> count = await repo.count_by_user(
            ...     user_id=uuid.uuid4(),
            ...     status="draft"
            ... )
        """
        filters = {"user_id": str(user_id)}
        if status:
            filters["status"] = status

        return await self.count(filters)

    async def archive(
        self,
        report_id: UUID,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Archive a report.

        Changes status to 'archived'.

        Args:
            report_id: Report UUID
            user_id: User UUID

        Returns:
            Updated report or None if not found

        Example:
            >>> report = await repo.archive(
            ...     report_id=uuid.uuid4(),
            ...     user_id=uuid.uuid4()
            ... )
        """
        return await self.update(
            report_id,
            {"status": "archived"}
        )

    async def unarchive(
        self,
        report_id: UUID,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Unarchive a report.

        Changes status back to 'completed'.

        Args:
            report_id: Report UUID
            user_id: User UUID

        Returns:
            Updated report or None if not found

        Example:
            >>> report = await repo.unarchive(
            ...     report_id=uuid.uuid4(),
            ...     user_id=uuid.uuid4()
            ... )
        """
        return await self.update(
            report_id,
            {"status": "completed"}
        )
