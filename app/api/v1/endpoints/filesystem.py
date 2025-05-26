from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends

from app.database.repositories import get_filesystem_repository
from app.database.repositories.filesystem_repository import FilesystemRepository
from app.models.file import FileCreate, FileModel, FileUpdate
from app.models.folder import Folder, FolderCreate, FolderUpdate
from app.services.filesystem_service import FilesystemService
from app.utils.auth import verify_jwt
from app.utils.response import success_response

router = APIRouter()


def get_filesystem_service(
    repository: FilesystemRepository = Depends(get_filesystem_repository),
) -> FilesystemService:
    return FilesystemService(repository)


@router.get("/folders", response_model=List[Folder])
async def get_folders(
    parent_id: Optional[UUID] = None,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    folders = filesystem_service.get_folders(user["sub"], parent_id)
    return success_response(folders)


@router.post("/folders", response_model=Folder)
async def create_folder(
    folder: FolderCreate,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    created_folder = filesystem_service.create_folder(folder, user["sub"])
    return success_response(created_folder)


@router.put("/folders/{folder_id}", response_model=Folder)
async def update_folder(
    folder_id: UUID,
    folder_update: FolderUpdate,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    updated_folder = filesystem_service.update_folder(
        folder_id, folder_update, user["sub"]
    )
    return success_response(updated_folder)


@router.delete("/folders/{folder_id}", response_model=Folder)
async def delete_folder(
    folder_id: UUID,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    deleted_folder = filesystem_service.delete_folder(folder_id, user["sub"])
    return success_response(deleted_folder)


@router.get("/files", response_model=List[FileModel])
async def get_files(
    folder_id: Optional[UUID] = None,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    files = filesystem_service.get_files(user["sub"], folder_id)
    return success_response(files)


@router.post("/files", response_model=FileModel)
async def create_file(
    file_data: FileCreate,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    created_file = filesystem_service.create_file(file_data, user["sub"])
    return success_response(created_file)


@router.get("/files/{file_id}", response_model=FileModel)
async def get_file(
    file_id: UUID,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    file = filesystem_service.get_file(file_id, user["sub"])
    return success_response(file)


@router.put("/files/{file_id}", response_model=FileModel)
async def update_file(
    file_id: UUID,
    file_update: FileUpdate,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    updated_file = filesystem_service.update_file(file_id, file_update, user["sub"])
    return success_response(updated_file)


@router.delete("/files/{file_id}", response_model=FileModel)
async def delete_file(
    file_id: UUID,
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    deleted_file = filesystem_service.delete_file(file_id, user["sub"])
    return success_response(deleted_file)


@router.get("/tree")
async def get_filesystem_tree(
    user: dict = Depends(verify_jwt),
    filesystem_service: FilesystemService = Depends(get_filesystem_service),
):
    tree = filesystem_service.get_filesystem_tree(user["sub"])
    return success_response(tree)
