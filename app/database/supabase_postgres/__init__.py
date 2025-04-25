# app/database/supabase_postgres/__init__.py

from typing import List, Optional
from uuid import UUID

from app.external.supabase import supabase
from app.models.file import FileCreate, FileModel, FileUpdate
from app.models.folder import Folder, FolderCreate, FolderUpdate
from app.utils.exceptions import DatabaseError, NotFoundError


class SupabasePostgres:
    def __init__(self):
        self.supabase = supabase

    def get_folders(
        self, user_id: str, parent_id: Optional[UUID] = None
    ) -> List[Folder]:
        try:
            query = self.supabase.table("folders").select("*").eq("user_id", user_id)
            if parent_id:
                query = query.eq("parent_id", str(parent_id))
            else:
                query = query.is_("parent_id", "null")
            return [Folder.model_validate(folder) for folder in query.execute().data]
        except Exception as e:
            raise DatabaseError("Error fetching folders", details={"error": str(e)})

    def folder_exists(
        self, user_id: str, name: str, parent_id: Optional[UUID] = None
    ) -> bool:
        try:
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
        except Exception as e:
            raise DatabaseError(
                "Error checking folder existence", details={"error": str(e)}
            )

    def create_folder(self, folder: FolderCreate, user_id: str) -> Folder:
        try:
            if self.folder_exists(user_id, folder.name, folder.parent_id):
                raise DatabaseError(
                    "Folder with the same name already exists in this location",
                    details={"error": "DUPLICATE_FOLDER"},
                )
            folder_data = folder.model_dump()
            folder_data["user_id"] = user_id
            if folder_data["parent_id"] is not None:
                folder_data["parent_id"] = str(folder_data["parent_id"])
            result = self.supabase.table("folders").insert(folder_data).execute()
            return Folder.model_validate(result.data[0])
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError("Error creating folder", details={"error": str(e)})

    def update_folder(
        self, folder_id: UUID, folder_update: FolderUpdate, user_id: str
    ) -> Optional[Folder]:
        try:
            update_data = folder_update.model_dump(exclude_unset=True)
            result = (
                self.supabase.table("folders")
                .update(update_data)
                .eq("id", str(folder_id))
                .eq("user_id", user_id)
                .execute()
            )
            if not result.data:
                raise NotFoundError(
                    "Folder not found or unauthorized",
                    details={"folder_id": str(folder_id)},
                )
            return Folder.model_validate(result.data[0])
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError("Error updating folder", details={"error": str(e)})

    def delete_folder(self, folder_id: UUID, user_id: str) -> Optional[Folder]:
        try:
            result = (
                self.supabase.table("folders")
                .delete()
                .eq("id", str(folder_id))
                .eq("user_id", user_id)
                .execute()
            )
            if not result.data:
                raise NotFoundError(
                    "Folder not found or unauthorized",
                    details={"folder_id": str(folder_id)},
                )
            return Folder.model_validate(result.data[0])
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError("Error deleting folder", details={"error": str(e)})

    def get_files(
        self, user_id: str, folder_id: Optional[UUID] = None
    ) -> List[FileModel]:
        try:
            query = self.supabase.table("files").select("*").eq("user_id", user_id)
            if folder_id:
                query = query.eq("folder_id", str(folder_id))
            else:
                query = query.is_("folder_id", "null")
            return [FileModel.model_validate(file) for file in query.execute().data]
        except Exception as e:
            raise DatabaseError("Error fetching files", details={"error": str(e)})

    def create_file(self, file_data: FileCreate) -> FileModel:
        try:
            data = file_data.model_dump()
            result = self.supabase.table("files").insert(data).execute()
            return FileModel.model_validate(result.data[0])
        except Exception as e:
            raise DatabaseError("Error creating file", details={"error": str(e)})

    def get_file(self, file_id: UUID, user_id: str) -> Optional[FileModel]:
        try:
            result = (
                self.supabase.table("files")
                .select("*")
                .eq("id", str(file_id))
                .eq("user_id", user_id)
                .execute()
            )
            if not result.data:
                raise NotFoundError(
                    "File not found or unauthorized", details={"file_id": str(file_id)}
                )
            return FileModel.model_validate(result.data[0])
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError("Error fetching file", details={"error": str(e)})

    def update_file(
        self, file_id: UUID, file_update: FileUpdate, user_id: str
    ) -> Optional[FileModel]:
        try:
            update_data = file_update.model_dump(exclude_unset=True)
            result = (
                self.supabase.table("files")
                .update(update_data)
                .eq("id", str(file_id))
                .eq("user_id", user_id)
                .execute()
            )
            if not result.data:
                raise NotFoundError(
                    "File not found or unauthorized", details={"file_id": str(file_id)}
                )
            return FileModel.model_validate(result.data[0])
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError("Error updating file", details={"error": str(e)})

    def delete_file(self, file_id: UUID, user_id: str) -> Optional[FileModel]:
        try:
            result = (
                self.supabase.table("files")
                .delete()
                .eq("id", str(file_id))
                .eq("user_id", user_id)
                .execute()
            )
            if not result.data:
                raise NotFoundError(
                    "File not found or unauthorized", details={"file_id": str(file_id)}
                )
            return FileModel.model_validate(result.data[0])
        except NotFoundError:
            raise
        except Exception as e:
            raise DatabaseError("Error deleting file", details={"error": str(e)})


def get_postgres() -> SupabasePostgres:
    return SupabasePostgres()
