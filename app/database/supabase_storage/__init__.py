# app/database/supabase_storage/__init__.py

import os
import time
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
            logger.info(f"Supabase storage bucket '{self.bucket_name}' initialized")
        except Exception as e:
            logger.error(f"Bucket {self.bucket_name} does not exist: {str(e)}")
            raise StorageError(
                f"Bucket {self.bucket_name} does not exist", details={"error": str(e)}
            )

    def _file_exists_in_bucket(self, storage_path: str) -> bool:
        try:
            response = self.supabase.storage.from_(self.bucket_name).list(
                path=storage_path
            )
            exists = any(
                file["name"] == os.path.basename(storage_path) for file in response
            )
            logger.debug(f"File existence check for {storage_path}: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking file existence in bucket: {str(e)}")
            return False

    async def upload_file(
        self,
        file_path: str,
        file_content: bytes,
        user_id: UUID,
        folder_id: Optional[UUID] = None,
    ) -> str:
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            if file_extension != ".tex":
                logger.warning(f"Invalid file type attempted: {file_path}")
                raise StorageError(
                    "Invalid file type",
                    details={"error": "Only .tex files are allowed"},
                )

            storage_path = f"{user_id}/"
            if folder_id:
                storage_path += f"{folder_id}/"
            storage_path += os.path.basename(file_path)

            if self._file_exists_in_bucket(storage_path):
                logger.warning(f"Duplicate file upload attempted: {storage_path}")
                raise StorageError(
                    "File with the same name already exists in this location",
                    details={"error": "DUPLICATE_FILE"},
                )

            self.supabase.storage.from_(self.bucket_name).upload(
                storage_path,
                file_content,
                {"content-type": "application/x-tex", "cache-control": "no-cache"},
            )
            logger.info(f"Successfully uploaded file: {storage_path}")
            return storage_path
        except StorageError:
            raise
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {str(e)}")
            raise StorageError("Error uploading file", details={"error": str(e)})

    async def download_file(self, storage_path: str) -> bytes:
        try:
            response = self.supabase.storage.from_(self.bucket_name).download(
                storage_path
            )
            logger.debug(f"Successfully downloaded file: {storage_path}")
            return response
        except Exception as e:
            logger.error(f"Error downloading file {storage_path}: {str(e)}")
            raise StorageError("Error downloading file", details={"error": str(e)})

    async def delete_file(self, storage_path: str) -> None:
        try:
            self.supabase.storage.from_(self.bucket_name).remove([storage_path])
            logger.info(f"Successfully deleted file: {storage_path}")
        except Exception as e:
            logger.error(f"Error deleting file {storage_path}: {str(e)}")
            raise StorageError("Error deleting file", details={"error": str(e)})

    async def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        try:
            response = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                storage_path, expires_in
            )
            logger.debug(f"Generated signed URL for file: {storage_path}")
            return response["signedURL"]
        except Exception as e:
            logger.error(f"Error generating URL for file {storage_path}: {str(e)}")
            raise StorageError("Error generating file URL", details={"error": str(e)})


def get_storage() -> SupabaseStorage:
    return SupabaseStorage()
