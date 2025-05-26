from fastapi import Depends

from app.database.repositories.filesystem_repository import FilesystemRepository
from app.database.supabase.filesystem import SupabaseFilesystem


def get_filesystem_repository(
    db: SupabaseFilesystem = Depends(lambda: SupabaseFilesystem()),
) -> FilesystemRepository:
    return FilesystemRepository(db)
