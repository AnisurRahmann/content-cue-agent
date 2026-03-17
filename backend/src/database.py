"""
Database Connection - Supabase Client

Initialize Supabase client for all database operations.
"""

from supabase import create_client, Client

from src.config import settings


def get_supabase() -> Client:
    """
    Get Supabase client instance.

    Returns:
        Supabase client for database operations
    """
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY
    )


# Global Supabase client instance
supabase: Client = get_supabase()
