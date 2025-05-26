from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends

from app.database.repositories.filesystem_repository import FilesystemRepository
from app.database.repositories.storage_repository import StorageRepository
from app.dependencies import get_filesystem_repository, get_storage_repository
from app.models.file import FileCreate, FileUpdate
from app.models.folder import FolderCreate, FolderUpdate
from app.services.filesystem_service import FilesystemService
from app.utils.auth import verify_jwt
from app.utils.response import success_response

router = APIRouter()


def get_filesystem_service(
    repository: FilesystemRepository = Depends(get_filesystem_repository),
    storage_repository: StorageRepository = Depends(get_storage_repository),
) -> FilesystemService:
    return FilesystemService(repository, storage_repository)


@router.get("/folders")
async def get_folders(
    parent_id: Optional[UUID] = None,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    folders = filesystem_service.get_folders(user["sub"], parent_id)
    return success_response(message="Folders retrieved successfully", data=folders)


@router.post("/folders")
async def create_folder(
    folder: FolderCreate,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    created_folder = filesystem_service.create_folder(folder, user["sub"])
    return success_response(message="Folder created successfully", data=created_folder)


@router.put("/folders/{folder_id}")
async def update_folder(
    folder_id: UUID,
    folder_update: FolderUpdate,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    updated_folder = filesystem_service.update_folder(
        folder_id, folder_update, user["sub"]
    )
    return success_response(message="Folder updated successfully", data=updated_folder)


@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: UUID,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    deleted_folder = filesystem_service.delete_folder(folder_id, user["sub"])
    return success_response(message="Folder deleted successfully", data=deleted_folder)


@router.get("/files")
async def get_files(
    folder_id: Optional[UUID] = None,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    files = filesystem_service.get_files(user["sub"], folder_id)
    return success_response(message="Files retrieved successfully", data=files)


@router.post("/files")
async def create_file(
    file_data: FileCreate,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    created_file = filesystem_service.create_file(file_data, user["sub"])
    return success_response(message="File created successfully", data=created_file)


@router.get("/files/{file_id}")
async def get_file(
    file_id: UUID,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    file = filesystem_service.get_file(file_id, user["sub"])
    return success_response(message="File retrieved successfully", data=file)


@router.put("/files/{file_id}")
async def update_file(
    file_id: UUID,
    file_update: FileUpdate,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    updated_file = filesystem_service.update_file(file_id, file_update, user["sub"])
    return success_response(message="File updated successfully", data=updated_file)


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: UUID,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    deleted_file = filesystem_service.delete_file(file_id, user["sub"])
    return success_response(message="File deleted successfully", data=deleted_file)


@router.get("/tree")
async def get_filesystem_tree(
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    tree = filesystem_service.get_filesystem_tree(user["sub"])
    return success_response(message="Filesystem tree retrieved successfully", data=tree)
