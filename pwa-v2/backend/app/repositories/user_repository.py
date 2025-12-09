"""
User Repository Module

Data access layer for users.
Handles all database operations for profiles table (users).

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from typing import Optional, Dict, Any
from uuid import UUID
from loguru import logger

from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """
    Repository for User entity.

    Provides CRUD operations and custom queries for users.
    Uses Supabase auth.users + public.profiles table.
    """

    TABLE_NAME = "profiles"

    async def find_by_email(
        self,
        email: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find user by email address.

        Args:
            email: User email

        Returns:
            User record or None if not found

        Example:
            >>> user = await repo.find_by_email("user@example.com")
        """
        try:
            response = (
                self.client
                .table(self.TABLE_NAME)
                .select("*")
                .eq("email", email)
                .maybe_single()
                .execute()
            )

            if response.data:
                logger.debug(f"User found with email: {email}")
            else:
                logger.debug(f"User not found with email: {email}")

            return response.data

        except Exception as e:
            logger.error(f"Error finding user by email {email}: {e}")
            raise

    async def email_exists(
        self,
        email: str
    ) -> bool:
        """
        Check if email already exists.

        Args:
            email: Email to check

        Returns:
            True if email exists, False otherwise

        Example:
            >>> exists = await repo.email_exists("user@example.com")
        """
        user = await self.find_by_email(email)
        return user is not None

    async def update_profile(
        self,
        user_id: UUID,
        profile_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update user profile information.

        Args:
            user_id: User UUID
            profile_data: Profile fields to update

        Returns:
            Updated user record or None if not found

        Example:
            >>> user = await repo.update_profile(
            ...     user_id=uuid.uuid4(),
            ...     profile_data={"full_name": "John Updated"}
            ... )
        """
        return await self.update(user_id, profile_data)

    async def update_avatar(
        self,
        user_id: UUID,
        avatar_url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update user avatar URL.

        Args:
            user_id: User UUID
            avatar_url: URL to avatar image

        Returns:
            Updated user record or None if not found

        Example:
            >>> user = await repo.update_avatar(
            ...     user_id=uuid.uuid4(),
            ...     avatar_url="https://example.com/avatar.jpg"
            ... )
        """
        return await self.update(
            user_id,
            {"avatar_url": avatar_url}
        )

    async def verify_email(
        self,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Mark user email as verified.

        Args:
            user_id: User UUID

        Returns:
            Updated user record or None if not found

        Example:
            >>> user = await repo.verify_email(uuid.uuid4())
        """
        return await self.update(
            user_id,
            {"email_verified": True}
        )

    async def get_stats(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get user statistics.

        Calls database function to calculate:
        - Total reports
        - Total receipts
        - Total value
        - Reports by status

        Args:
            user_id: User UUID

        Returns:
            Dict with user statistics

        Example:
            >>> stats = await repo.get_stats(uuid.uuid4())
            {
                "total_reports": 10,
                "total_receipts": 45,
                "total_value": 5432.10,
                "reports_by_status": {...}
            }
        """
        try:
            response = (
                self.client
                .rpc(
                    "get_user_stats",
                    {"p_user_id": str(user_id)}
                )
                .execute()
            )

            logger.info(f"Stats retrieved for user {user_id}")
            return response.data

        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {e}")
            # Return empty stats on error
            return {
                "total_reports": 0,
                "total_receipts": 0,
                "total_value": 0,
                "reports_by_status": {}
            }
