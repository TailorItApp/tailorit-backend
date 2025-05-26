# app/external/supabase/__init__.py

from app.config import settings
from app.utils.logger import logger
from supabase import Client, create_client


class SupabaseClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            try:
                if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                    logger.error("Supabase URL and Key must be configured in settings")
                    raise ValueError(
                        "Supabase URL and Key must be configured in settings"
                    )

                self._client = create_client(
                    settings.SUPABASE_URL, settings.SUPABASE_KEY
                )
                logger.info("Successfully initialized Supabase client")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise

    @property
    def client(self) -> Client:
        return self._client


supabase = SupabaseClient().client
