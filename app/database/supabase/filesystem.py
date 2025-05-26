from typing import List, Optional
from uuid import UUID

from app.external.supabase import get_supabase_client


class SupabaseFilesystem:
    def __init__(self):
        self.supabase = get_supabase_client()

    # ==================== FOLDER OPERATIONS ====================
    def get_folders(self, user_id: str, parent_id: Optional[UUID] = None) -> List[dict]:
        query = self.supabase.table("folders").select("*").eq("user_id", user_id)
        query = (
            query.is_("parent_id", None)
            if parent_id is None
            else query.eq("parent_id", str(parent_id))
        )
        return query.execute().data or []

    def get_folder(self, folder_id: UUID, user_id: str) -> Optional[dict]:
        result = (
            self.supabase.table("folders")
            .select("*")
            .eq("id", str(folder_id))
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def create_folder(self, folder_data: dict) -> dict:
        result = self.supabase.table("folders").insert(folder_data).execute()
        return result.data[0]

    def update_folder(
        self, folder_id: UUID, user_id: str, update_data: dict
    ) -> Optional[dict]:
        result = (
            self.supabase.table("folders")
            .update(update_data)
            .eq("id", str(folder_id))
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def delete_folder(self, folder_id: UUID, user_id: str) -> Optional[dict]:
        result = (
            self.supabase.table("folders")
            .delete()
            .eq("id", str(folder_id))
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def folder_exists(
        self, user_id: str, name: str, parent_id: Optional[UUID] = None
    ) -> bool:
        query = (
            self.supabase.table("folders")
            .select("*")
            .eq("user_id", user_id)
            .eq("name", name)
        )
        if parent_id:
            query = query.eq("parent_id", str(parent_id))
        else:
            query = query.is_("parent_id", "null")
        result = query.execute()
        return len(result.data) > 0

    # ==================== FILE OPERATIONS ====================
    def get_files(self, user_id: str, folder_id: Optional[UUID] = None) -> List[dict]:
        query = self.supabase.table("files").select("*").eq("user_id", user_id)
        if folder_id:
            query = query.eq("folder_id", str(folder_id))
        return query.execute().data or []

    def get_file(self, file_id: UUID, user_id: str) -> Optional[dict]:
        result = (
            self.supabase.table("files")
            .select("*")
            .eq("id", str(file_id))
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def create_file(self, file_data: dict) -> dict:
        result = self.supabase.table("files").insert(file_data).execute()
        return result.data[0]

    def update_file(
        self, file_id: UUID, user_id: str, update_data: dict
    ) -> Optional[dict]:
        result = (
            self.supabase.table("files")
            .update(update_data)
            .eq("id", str(file_id))
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def delete_file(self, file_id: UUID, user_id: str) -> Optional[dict]:
        result = (
            self.supabase.table("files")
            .delete()
            .eq("id", str(file_id))
            .eq("user_id", user_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def file_exists(
        self, user_id: str, name: str, folder_id: Optional[UUID] = None
    ) -> bool:
        query = (
            self.supabase.table("files")
            .select("*")
            .eq("user_id", user_id)
            .eq("name", name)
        )
        if folder_id:
            query = query.eq("folder_id", str(folder_id))
        else:
            query = query.is_("folder_id", "null")
        result = query.execute()
        return len(result.data) > 0
