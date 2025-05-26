# app/external/supabase/__init__.py

from functools import lru_cache

from app.config import settings
from app.utils.logger import logger
from supabase import Client, create_client


@lru_cache()
def get_supabase_client() -> Client:
    """
    Cached dependency that creates a Supabase client.
    Uses lru_cache to ensure we only create one client per process,
    but still allows for dependency injection and testing.
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.error("Supabase URL and Key must be configured in settings")
            raise ValueError("Supabase URL and Key must be configured in settings")

        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Successfully created Supabase client")
        return client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {str(e)}")
        raise
