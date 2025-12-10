"""
Supabase Client Module

Provides configured Supabase client instances for database and storage operations.
Uses service role key for backend operations (bypasses RLS when needed).

Author: RelatoRecibo Team
Created: 2025-12-09
"""

from supabase import create_client, Client
from loguru import logger

from app.config import settings


class SupabaseClient:
    """
    Supabase client singleton.

    Provides access to Supabase database and storage.
    Uses service role key for server-side operations.

    Usage:
        from app.repositories.supabase_client import get_supabase_client

        client = get_supabase_client()
        response = client.table('reports').select('*').execute()
    """

    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        """
        Get or create Supabase client instance.

        Returns:
            Client: Configured Supabase client

        Note:
            Uses service role key for backend operations.
            This bypasses Row Level Security (RLS) when needed.
            Always validate user permissions in your service layer.
        """
        if cls._instance is None:
            try:
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise

        return cls._instance

    @classmethod
    def close(cls):
        """Close Supabase client connection."""
        if cls._instance is not None:
            # Supabase client doesn't need explicit closing
            # But we reset the instance
            cls._instance = None
            logger.info("Supabase client closed")


# ----------------------------------------
# Global client getter
# ----------------------------------------
def get_supabase_client() -> Client:
    """
    Get configured Supabase client.

    Returns:
        Client: Supabase client instance

    Example:
        >>> client = get_supabase_client()
        >>> response = client.table('reports').select('*').execute()
    """
    return SupabaseClient.get_client()


# ----------------------------------------
# Convenience client instance
# ----------------------------------------
# Note: Client is created lazily via get_supabase_client()
# Do not initialize here to avoid import-time errors
