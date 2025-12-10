"""
Base Repository Module

Provides abstract base class for all repositories.
Implements common database operations using Supabase.

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from abc import ABC, abstractmethod
from supabase import Client
from loguru import logger

from app.repositories.supabase_client import get_supabase_client


class BaseRepository(ABC):
    """
    Abstract base repository class.

    Provides common CRUD operations for all entities.
    Subclasses must define TABLE_NAME constant.

    Usage:
        class ReportRepository(BaseRepository):
            TABLE_NAME = "reports"

            async def find_by_user(self, user_id: UUID):
                # Custom method
                pass
    """

    TABLE_NAME: str = None  # Must be overridden in subclass

    def __init__(self, client: Optional[Client] = None):
        """
        Initialize repository with Supabase client.

        Args:
            client: Optional Supabase client (uses default if not provided)
        """
        if self.TABLE_NAME is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define TABLE_NAME"
            )

        self.client = client or get_supabase_client()
        logger.debug(f"Repository initialized for table: {self.TABLE_NAME}")

    # ----------------------------------------
    # Basic CRUD Operations
    # ----------------------------------------

    async def find_by_id(
        self,
        id: UUID,
        columns: str = "*"
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single record by ID.

        Args:
            id: Record UUID
            columns: Columns to select (default: "*")

        Returns:
            Dict with record data or None if not found

        Example:
            >>> record = await repo.find_by_id(uuid.uuid4())
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .select(columns)
                .eq("id", str(id))
                .maybe_single()
                .execute()
            )

            if response and response.data:
                logger.debug(f"Record found in {self.TABLE_NAME}: {id}")
                return response.data
            else:
                logger.debug(f"Record not found in {self.TABLE_NAME}: {id}")
                return None

        except Exception as e:
            logger.error(f"Error finding record in {self.TABLE_NAME}: {e}")
            raise

    async def find_all(
        self,
        columns: str = "*",
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find all records with pagination.

        Args:
            columns: Columns to select
            limit: Maximum number of records
            offset: Number of records to skip
            order_by: Column to order by
            ascending: Sort order (default: descending)

        Returns:
            List of records

        Example:
            >>> records = await repo.find_all(limit=20, offset=0)
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .select(columns)
                .order(order_by, desc=not ascending)
                .range(offset, offset + limit - 1)
                .execute()
            )

            logger.debug(
                f"Found {len(response.data)} records in {self.TABLE_NAME}"
            )
            return response.data

        except Exception as e:
            logger.error(f"Error finding all records in {self.TABLE_NAME}: {e}")
            raise

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record.

        Args:
            data: Record data to insert

        Returns:
            Created record with generated fields (id, timestamps)

        Example:
            >>> record = await repo.create({"name": "Test", "user_id": "..."})
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .insert(data)
                .execute()
            )

            if not response or not response.data or len(response.data) == 0:
                logger.error(f"No data returned from insert in {self.TABLE_NAME}")
                raise ValueError(f"Failed to create record in {self.TABLE_NAME}: no data returned")

            created_record = response.data[0]
            logger.info(
                f"Record created in {self.TABLE_NAME}: {created_record.get('id')}"
            )

            return created_record

        except Exception as e:
            logger.error(f"Error creating record in {self.TABLE_NAME}: {e}")
            raise

    async def update(
        self,
        id: UUID,
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing record.

        Args:
            id: Record UUID
            data: Fields to update

        Returns:
            Updated record or None if not found

        Note:
            The 'updated_at' field is automatically updated by database trigger.

        Example:
            >>> record = await repo.update(uuid.uuid4(), {"name": "New Name"})
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .update(data)
                .eq("id", str(id))
                .execute()
            )

            if not response.data:
                logger.warning(
                    f"Record not found for update in {self.TABLE_NAME}: {id}"
                )
                return None

            updated_record = response.data[0]
            logger.info(f"Record updated in {self.TABLE_NAME}: {id}")

            return updated_record

        except Exception as e:
            logger.error(f"Error updating record in {self.TABLE_NAME}: {e}")
            raise

    async def delete(self, id: UUID) -> bool:
        """
        Delete a record by ID.

        Args:
            id: Record UUID

        Returns:
            True if deleted, False if not found

        Example:
            >>> deleted = await repo.delete(uuid.uuid4())
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .delete()
                .eq("id", str(id))
                .execute()
            )

            if response.data:
                logger.info(f"Record deleted from {self.TABLE_NAME}: {id}")
                return True
            else:
                logger.warning(
                    f"Record not found for deletion in {self.TABLE_NAME}: {id}"
                )
                return False

        except Exception as e:
            logger.error(f"Error deleting record from {self.TABLE_NAME}: {e}")
            raise

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters.

        Args:
            filters: Optional dict of column:value filters

        Returns:
            Total count of records

        Example:
            >>> count = await repo.count({"status": "active"})
        """
        try:
            query = self.client.table(self.TABLE_NAME).select("id", count="exact")

            # Apply filters
            if filters:
                for column, value in filters.items():
                    query = query.eq(column, value)

            response = query.execute()
            
            # Try to get count from response
            if hasattr(response, "count") and response.count is not None:
                count = response.count
            elif hasattr(response, "data"):
                # Fallback: count the data array length
                count = len(response.data) if response.data else 0
            else:
                count = 0

            logger.debug(f"Count in {self.TABLE_NAME}: {count}")
            return count

        except Exception as e:
            logger.error(f"Error counting records in {self.TABLE_NAME}: {e}")
            raise

    # ----------------------------------------
    # Utility Methods
    # ----------------------------------------

    async def exists(self, id: UUID) -> bool:
        """
        Check if a record exists.

        Args:
            id: Record UUID

        Returns:
            True if exists, False otherwise

        Example:
            >>> exists = await repo.exists(uuid.uuid4())
        """
        record = await self.find_by_id(id, columns="id")
        return record is not None
