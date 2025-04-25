# app/external/supabase/__init__.py

from app.config import settings
from app.utils.logger import logger
from supabase import Client, create_client

try:
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        logger.error("Supabase URL and Key must be configured in settings")
        raise ValueError("Supabase URL and Key must be configured in settings")

    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    logger.info("Successfully initialized Supabase client")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    raise
