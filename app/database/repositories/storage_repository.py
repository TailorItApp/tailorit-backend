from typing import Optional
from uuid import UUID

from app.database.supabase.storage import SupabaseStorage
from app.utils.decorators import db_error_handler


class StorageRepository:
    def __init__(self, storage: SupabaseStorage):
        self.storage = storage

    @db_error_handler
    async def upload_file(
        self,
        file_path: str,
        file_content: bytes,
        user_id: UUID,
        folder_id: Optional[UUID] = None,
    ) -> str:
        return await self.storage.upload_file(
            file_path, file_content, user_id, folder_id
        )

    @db_error_handler
    async def download_file(self, storage_path: str) -> bytes:
        return await self.storage.download_file(storage_path)

    @db_error_handler
    async def delete_file(self, storage_path: str) -> None:
        await self.storage.delete_file(storage_path)

    @db_error_handler
    async def get_file_url(self, storage_path: str, expires_in: int = 3600) -> str:
        return await self.storage.get_file_url(storage_path, expires_in)

    def get_storage_path(
        self, file_path: str, user_id: UUID, folder_id: Optional[UUID] = None
    ) -> str:
        return self.storage._get_storage_path(file_path, user_id, folder_id)
