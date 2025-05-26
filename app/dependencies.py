from typing import Annotated

from fastapi import Depends

from app.database.repositories.filesystem_repository import FilesystemRepository
from app.database.repositories.storage_repository import StorageRepository
from app.database.supabase.filesystem import SupabaseFilesystem
from app.database.supabase.storage import SupabaseStorage
from app.services.filesystem_service import FilesystemService


def get_supabase_filesystem() -> SupabaseFilesystem:
    return SupabaseFilesystem()


def get_supabase_storage() -> SupabaseStorage:
    return SupabaseStorage()


def get_filesystem_repository(
    filesystem: SupabaseFilesystem = Depends(get_supabase_filesystem),
) -> FilesystemRepository:
    return FilesystemRepository(filesystem)


def get_storage_repository(
    storage: SupabaseStorage = Depends(get_supabase_storage),
) -> StorageRepository:
    return StorageRepository(storage)


def get_filesystem_service(
    filesystem_repository: FilesystemRepository = Depends(get_filesystem_repository),
    storage_repository: StorageRepository = Depends(get_storage_repository),
) -> FilesystemService:
    return FilesystemService(filesystem_repository, storage_repository)


# Dependency types for use in route handlers
FilesystemServiceDep = Annotated[FilesystemService, Depends(get_filesystem_service)]
