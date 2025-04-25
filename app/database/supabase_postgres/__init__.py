# app/database/supabase_postgres/__init__.py

from collections import deque
from typing import List, Optional
from uuid import UUID

from app.external.supabase import supabase
from app.models.file import FileCreate, FileModel, FileUpdate
from app.models.folder import Folder, FolderCreate, FolderUpdate
from app.utils.exceptions import DatabaseError, NotFoundError
from app.utils.logger import logger


class SupabasePostgres:
    def __init__(self):
        self.supabase = supabase

    def get_folders(
        self, user_id: str, parent_id: Optional[UUID] = None
    ) -> List[Folder]:
        try:
            query = self.supabase.table("folders").select("*").eq("user_id", user_id)

            if parent_id is None:
                query = query.is_("parent_id", None)
            else:
                query = query.eq("parent_id", str(parent_id))

            response = query.execute()
            rows = response.data or []
            folders = [Folder.model_validate(r) for r in rows]

            logger.debug(
                f"Retrieved {len(folders)} folders for user {user_id}. Parent ID: {parent_id}"
            )
            return folders

        except Exception as e:
            logger.error(f"Error fetching folders for user {user_id}: {e}")
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
            exists = len(result.data) > 0
            logger.debug(f"Folder existence check for {name}: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking folder existence: {str(e)}")
            raise DatabaseError(
                "Error checking folder existence", details={"error": str(e)}
            )

    def create_folder(self, folder: FolderCreate, user_id: str) -> Folder:
        try:
            if self.folder_exists(user_id, folder.name, folder.parent_id):
                logger.warning(f"Duplicate folder creation attempted: {folder.name}")
                raise DatabaseError(
                    "Folder with the same name already exists in this location",
                    details={"error": "DUPLICATE_FOLDER"},
                )
            folder_data = folder.model_dump()
            folder_data["user_id"] = user_id
            if folder_data["parent_id"] is not None:
                folder_data["parent_id"] = str(folder_data["parent_id"])
            result = self.supabase.table("folders").insert(folder_data).execute()
            created_folder = Folder.model_validate(result.data[0])
            logger.info(f"Created folder: {created_folder.name} for user {user_id}")
            return created_folder
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            raise DatabaseError("Error creating folder", details={"error": str(e)})

    def update_folder(
        self, folder_id: UUID, folder_update: FolderUpdate, user_id: str
    ) -> Optional[Folder]:
        try:
            update_data = folder_update.model_dump(exclude_unset=True)
            if "parent_id" in update_data and update_data["parent_id"] is not None:
                update_data["parent_id"] = str(update_data["parent_id"])
            result = (
                self.supabase.table("folders")
                .update(update_data)
                .eq("id", str(folder_id))
                .eq("user_id", user_id)
                .execute()
            )
            if not result.data:
                logger.warning(f"Folder not found for update: {folder_id}")
                raise NotFoundError(
                    "Folder not found or unauthorized",
                    details={"folder_id": str(folder_id)},
                )
            updated_folder = Folder.model_validate(result.data[0])
            logger.info(f"Updated folder: {updated_folder.name}")
            return updated_folder
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating folder {folder_id}: {str(e)}")
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
                logger.warning(f"Folder not found for deletion: {folder_id}")
                raise NotFoundError(
                    "Folder not found or unauthorized",
                    details={"folder_id": str(folder_id)},
                )
            deleted_folder = Folder.model_validate(result.data[0])
            logger.info(f"Deleted folder: {deleted_folder.name}")
            return deleted_folder
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting folder {folder_id}: {str(e)}")
            raise DatabaseError("Error deleting folder", details={"error": str(e)})

    def get_files(
        self, user_id: str, folder_id: Optional[UUID] = None
    ) -> List[FileModel]:
        try:
            query = self.supabase.table("files").select("*").eq("user_id", user_id)
            if folder_id:
                query = query.eq("folder_id", str(folder_id))
            files = [FileModel.model_validate(file) for file in query.execute().data]
            logger.debug(f"Retrieved {len(files)} files for user {user_id}")
            return files
        except Exception as e:
            logger.error(f"Error fetching files for user {user_id}: {str(e)}")
            raise DatabaseError("Error fetching files", details={"error": str(e)})

    def file_exists(
        self, user_id: str, name: str, folder_id: Optional[UUID] = None
    ) -> bool:
        try:
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
            exists = len(result.data) > 0
            logger.debug(f"File existence check for {name}: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking file existence: {str(e)}")
            raise DatabaseError(
                "Error checking file existence", details={"error": str(e)}
            )

    def create_file(self, file_data: FileCreate, user_id: str) -> FileModel:
        try:
            if self.file_exists(user_id, file_data.name, file_data.folder_id):
                logger.warning(f"Duplicate file creation attempted: {file_data.name}")
                raise DatabaseError(
                    "File with the same name already exists in this folder",
                    details={"error": "DUPLICATE_FILE"},
                )
            data = file_data.model_dump()
            data["user_id"] = user_id
            result = self.supabase.table("files").insert(data).execute()
            created_file = FileModel.model_validate(result.data[0])
            logger.info(f"Created file: {created_file.name} for user {user_id}")
            return created_file
        except DatabaseError:
            raise
        except Exception as e:
            logger.error(f"Error creating file: {str(e)}")
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
                logger.warning(f"File not found: {file_id}")
                raise NotFoundError(
                    "File not found or unauthorized", details={"file_id": str(file_id)}
                )
            file = FileModel.model_validate(result.data[0])
            logger.debug(f"Retrieved file: {file.name}")
            return file
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching file {file_id}: {str(e)}")
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
                logger.warning(f"File not found for update: {file_id}")
                raise NotFoundError(
                    "File not found or unauthorized", details={"file_id": str(file_id)}
                )
            updated_file = FileModel.model_validate(result.data[0])
            logger.info(f"Updated file: {updated_file.name}")
            return updated_file
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating file {file_id}: {str(e)}")
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
                logger.warning(f"File not found for deletion: {file_id}")
                raise NotFoundError(
                    "File not found or unauthorized", details={"file_id": str(file_id)}
                )
            deleted_file = FileModel.model_validate(result.data[0])
            logger.info(f"Deleted file: {deleted_file.name}")
            return deleted_file
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {str(e)}")
            raise DatabaseError("Error deleting file", details={"error": str(e)})

    def get_all_folders_recursive(self, user_id: str) -> List[Folder]:
        all_folders: List[Folder] = []
        queue = deque([None])

        while queue:
            parent_id = queue.popleft()
            children = self.get_folders(user_id, parent_id)
            all_folders.extend(children)
            queue.extend(child.id for child in children)

        return all_folders

    def get_filesystem_tree(self, user_id: str) -> dict:
        all_folders = self.get_all_folders_recursive(user_id)
        all_files = self.get_files(user_id)

        files_by_folder = {}
        for f in all_files:
            key = str(f.folder_id) if f.folder_id else "root"
            files_by_folder.setdefault(key, []).append(f)

        folder_dicts = {}
        for folder in all_folders:
            folder_dicts[str(folder.id)] = {
                **folder.model_dump(),
                "files": files_by_folder.get(str(folder.id), []),
                "subfolders": [],
            }

        tree = {"folders": [], "files": files_by_folder.get("root", [])}

        for folder in all_folders:
            d = folder_dicts[str(folder.id)]
            if folder.parent_id:
                parent = folder_dicts.get(str(folder.parent_id))
                if parent:
                    parent["subfolders"].append(d)
            else:
                tree["folders"].append(d)

        return tree


def get_postgres() -> SupabasePostgres:
    return SupabasePostgres()
