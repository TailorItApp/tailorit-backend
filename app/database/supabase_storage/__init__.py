# app/database/supabase_storage/__init__.py

import os
from typing import Optional
from uuid import UUID

from app.config import settings
from app.external.supabase import supabase
from app.utils.exceptions import StorageError
from app.utils.logger import logger


class SupabaseStorage:
    def __init__(self):
        self.supabase = supabase
        self.bucket_name = settings.SUPABASE_STORAGE_BUCKET
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            self.supabase.storage.get_bucket(self.bucket_name)
            logger.info("Supabase storage initialized")
        except Exception as e:
            logger.error(f"Bucket {self.bucket_name} does not exist")
            raise StorageError(
                f"Bucket {self.bucket_name} does not exist", details={"error": str(e)}
            )

    async def upload_file(
        self,
        file_path: str,
        file_content: bytes,
        user_id: UUID,
        folder_id: Optional[UUID] = None,
    ) -> str:
        try:
            storage_path = f"{user_id}/"
            if folder_id:
                storage_path += f"{folder_id}/"
            storage_path += os.path.basename(file_path)

            self.supabase.storage.from_(self.bucket_name).upload(
                storage_path,
                file_content,
                {"content-type": "application/octet-stream"},
            )

            return storage_path
        except Exception as e:
            raise StorageError("Error uploading file", details={"error": str(e)})

    async def download_file(self, storage_path: str) -> bytes:
        try:
            response = self.supabase.storage.from_(self.bucket_name).download(
                storage_path
            )
            return response
        except Exception as e:
            raise StorageError("Error downloading file", details={"error": str(e)})

    async def delete_file(self, storage_path: str) -> None:
        try:
            self.supabase.storage.from_(self.bucket_name).remove([storage_path])
        except Exception as e:
            raise StorageError("Error deleting file", details={"error": str(e)})

    async def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        try:
            response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                storage_path, expires_in
            )
            return response["signedURL"]
        except Exception as e:
            raise StorageError("Error generating file URL", details={"error": str(e)})


def get_storage() -> SupabaseStorage:
    return SupabaseStorage()
