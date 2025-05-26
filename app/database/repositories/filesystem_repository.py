from typing import List, Optional
from uuid import UUID

from app.database.supabase.filesystem import SupabaseFilesystem
from app.utils.decorators import db_error_handler


class FilesystemRepository:
    def __init__(self, db: SupabaseFilesystem):
        self.db = db

    # ==================== FOLDER OPERATIONS ====================
    @db_error_handler
    def get_folders(self, user_id: str, parent_id: Optional[UUID] = None) -> List[dict]:
        return self.db.get_folders(user_id, parent_id)

    @db_error_handler
    def get_folder(self, folder_id: UUID, user_id: str) -> Optional[dict]:
        return self.db.get_folder(folder_id, user_id)

    @db_error_handler
    def create_folder(self, folder_data: dict) -> dict:
        return self.db.create_folder(folder_data)

    @db_error_handler
    def update_folder(
        self, folder_id: UUID, user_id: str, update_data: dict
    ) -> Optional[dict]:
        return self.db.update_folder(folder_id, user_id, update_data)

    @db_error_handler
    def delete_folder(self, folder_id: UUID, user_id: str) -> Optional[dict]:
        return self.db.delete_folder(folder_id, user_id)

    @db_error_handler
    def folder_exists(
        self, user_id: str, name: str, parent_id: Optional[UUID] = None
    ) -> bool:
        return self.db.folder_exists(user_id, name, parent_id)

    @db_error_handler
    def get_files(self, user_id: str, folder_id: Optional[UUID] = None) -> List[dict]:
        return self.db.get_files(user_id, folder_id)

    # ==================== FILE OPERATIONS ====================
    @db_error_handler
    def get_file(self, file_id: UUID, user_id: str) -> Optional[dict]:
        return self.db.get_file(file_id, user_id)

    @db_error_handler
    def create_file(self, file_data: dict) -> dict:
        return self.db.create_file(file_data)

    @db_error_handler
    def update_file(
        self, file_id: UUID, user_id: str, update_data: dict
    ) -> Optional[dict]:
        return self.db.update_file(file_id, user_id, update_data)

    @db_error_handler
    def delete_file(self, file_id: UUID, user_id: str) -> Optional[dict]:
        return self.db.delete_file(file_id, user_id)

    @db_error_handler
    def file_exists(
        self, user_id: str, name: str, folder_id: Optional[UUID] = None
    ) -> bool:
        return self.db.file_exists(user_id, name, folder_id)
