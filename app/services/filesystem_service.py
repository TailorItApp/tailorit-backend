# app/services/filesystem_service.py

from collections import deque
from typing import List, Optional
from uuid import UUID

from app.database.repositories.filesystem_repository import FilesystemRepository
from app.database.repositories.storage_repository import StorageRepository
from app.models.file import FileCreate, FileModel, FileUpdate
from app.models.folder import Folder, FolderCreate, FolderUpdate
from app.utils.decorators import db_error_handler
from app.utils.exceptions import DatabaseError, NotFoundError
from app.utils.logger import logger


class FilesystemService:
    def __init__(
        self,
        repository: FilesystemRepository,
        storage_repository: StorageRepository,
    ):
        self.repository = repository
        self.storage = storage_repository

    @db_error_handler
    def get_folders(
        self, user_id: str, parent_id: Optional[UUID] = None
    ) -> List[Folder]:
        rows = self.repository.get_folders(user_id, parent_id)
        folders = [Folder.model_validate(r) for r in rows]
        logger.debug(
            f"Retrieved {len(folders)} folders for user {user_id}. Parent ID: {parent_id}"
        )

        return folders

    @db_error_handler
    def folder_exists(
        self, user_id: str, name: str, parent_id: Optional[UUID] = None
    ) -> bool:
        exists = self.repository.folder_exists(user_id, name, parent_id)
        logger.debug(f"Folder existence check for {name}: {exists}")

        return exists

    @db_error_handler
    def create_folder(self, folder: FolderCreate, user_id: str) -> Folder:
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

        result = self.repository.create_folder(folder_data)
        created_folder = Folder.model_validate(result)
        logger.info(f"Created folder: {created_folder.name} for user {user_id}")

        return created_folder

    @db_error_handler
    def update_folder(
        self, folder_id: UUID, folder_update: FolderUpdate, user_id: str
    ) -> Optional[Folder]:
        update_data = folder_update.model_dump(exclude_unset=True)
        if "parent_id" in update_data and update_data["parent_id"] is not None:
            update_data["parent_id"] = str(update_data["parent_id"])
        result = self.repository.update_folder(folder_id, user_id, update_data)
        if not result:
            logger.warning(f"Folder not found for update: {folder_id}")
            raise NotFoundError(
                "Folder not found or unauthorized",
                details={"folder_id": str(folder_id)},
            )
        updated_folder = Folder.model_validate(result)
        logger.info(f"Updated folder: {updated_folder.name}")
        return updated_folder

    @db_error_handler
    def delete_folder(self, folder_id: UUID, user_id: str) -> Optional[Folder]:
        result = self.repository.delete_folder(folder_id, user_id)
        if not result:
            logger.warning(f"Folder not found for deletion: {folder_id}")
            raise NotFoundError(
                "Folder not found or unauthorized",
                details={"folder_id": str(folder_id)},
            )
        deleted_folder = Folder.model_validate(result)
        logger.info(f"Deleted folder: {deleted_folder.name}")
        return deleted_folder

    @db_error_handler
    def get_files(
        self, user_id: str, folder_id: Optional[UUID] = None
    ) -> List[FileModel]:
        files_data = self.repository.get_files(user_id, folder_id)
        files = [FileModel.model_validate(file) for file in files_data]
        logger.debug(f"Retrieved {len(files)} files for user {user_id}")
        return files

    @db_error_handler
    def file_exists(
        self, user_id: str, name: str, folder_id: Optional[UUID] = None
    ) -> bool:
        exists = self.repository.file_exists(user_id, name, folder_id)
        logger.debug(f"File existence check for {name}: {exists}")
        return exists

    @db_error_handler
    async def create_file(
        self, file_data: FileCreate, user_id: str, file_content: bytes
    ) -> FileModel:
        if self.file_exists(user_id, file_data.name, file_data.folder_id):
            logger.warning(f"Duplicate file creation attempted: {file_data.name}")
            raise DatabaseError(
                "File with the same name already exists in this folder",
                details={"error": "DUPLICATE_FILE"},
            )

        # First upload the file to storage
        storage_path = await self.storage.upload_file(
            file_data.name,
            file_content,
            UUID(user_id),
            file_data.folder_id,
        )

        # Then create the database entry
        data = file_data.model_dump()
        data["user_id"] = user_id
        data["storage_path"] = storage_path
        result = self.repository.create_file(data)
        created_file = FileModel.model_validate(result)
        logger.info(f"Created file: {created_file.name} for user {user_id}")
        return created_file

    @db_error_handler
    def get_file(self, file_id: UUID, user_id: str) -> Optional[FileModel]:
        result = self.repository.get_file(file_id, user_id)
        if not result:
            logger.warning(f"File not found: {file_id}")
            raise NotFoundError(
                "File not found or unauthorized", details={"file_id": str(file_id)}
            )
        file = FileModel.model_validate(result)
        logger.debug(f"Retrieved file: {file.name}")
        return file

    @db_error_handler
    async def update_file(
        self,
        file_id: UUID,
        file_update: FileUpdate,
        user_id: str,
        file_content: Optional[bytes] = None,
    ) -> Optional[FileModel]:
        # Get the current file to check if it exists and get its storage path
        current_file = self.get_file(file_id, user_id)

        update_data = file_update.model_dump(exclude_unset=True)

        # If new file content is provided, update the storage
        if file_content is not None:
            storage_path = await self.storage.upload_file(
                current_file.name,
                file_content,
                UUID(user_id),
                current_file.folder_id,
            )
            update_data["storage_path"] = storage_path

        result = self.repository.update_file(file_id, user_id, update_data)
        if not result:
            logger.warning(f"File not found for update: {file_id}")
            raise NotFoundError(
                "File not found or unauthorized", details={"file_id": str(file_id)}
            )
        updated_file = FileModel.model_validate(result)
        logger.info(f"Updated file: {updated_file.name}")
        return updated_file

    @db_error_handler
    async def delete_file(self, file_id: UUID, user_id: str) -> Optional[FileModel]:
        # Get the file first to get its storage path
        file = self.get_file(file_id, user_id)

        # Delete from storage
        await self.storage.delete_file(file.storage_path)

        # Delete from database
        result = self.repository.delete_file(file_id, user_id)
        if not result:
            logger.warning(f"File not found for deletion: {file_id}")
            raise NotFoundError(
                "File not found or unauthorized", details={"file_id": str(file_id)}
            )
        deleted_file = FileModel.model_validate(result)
        logger.info(f"Deleted file: {deleted_file.name}")
        return deleted_file

    @db_error_handler
    async def download_file(self, file_id: UUID, user_id: str) -> bytes:
        file = self.get_file(file_id, user_id)
        return await self.storage.download_file(file.storage_path)

    @db_error_handler
    async def get_file_url(
        self, file_id: UUID, user_id: str, expires_in: int = 3600
    ) -> str:
        file = self.get_file(file_id, user_id)
        return await self.storage.get_file_url(file.storage_path, expires_in)

    @db_error_handler
    def get_all_folders_recursive(self, user_id: str) -> List[Folder]:
        all_folders: List[Folder] = []
        queue = deque([None])

        while queue:
            parent_id = queue.popleft()
            children = self.get_folders(user_id, parent_id)
            all_folders.extend(children)
            queue.extend(child.id for child in children)

        return all_folders

    @db_error_handler
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
