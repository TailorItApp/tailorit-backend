# app/api/endpoints/folders.py

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query

from app.database.supabase_postgres import SupabasePostgres, get_postgres
from app.models.folder import FolderCreate, FolderUpdate
from app.utils.auth import verify_jwt
from app.utils.exceptions import DatabaseError, NotFoundError
from app.utils.response import success_response

router = APIRouter()


@router.get("", status_code=200)
async def get_folders(
    parent_id: Optional[UUID] = Query(
        None,
        description="Only return folders whose parent_id matches this UUID; omit for root-level",
    ),
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
):
    try:
        folders = postgres.get_folders(str(user["sub"]), parent_id)
        return success_response(message="Folders fetched successfully", data=folders)
    except Exception as e:
        raise DatabaseError("Error fetching folders", details={"error": str(e)})


@router.post("", status_code=201)
async def create_folder(
    folder: FolderCreate = Body(...),
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
):
    try:
        created_folder = postgres.create_folder(folder, str(user["sub"]))
        return success_response(
            message="Folder created successfully", data=created_folder
        )
    except DatabaseError as e:
        if e.details and e.details.get("error") == "DUPLICATE_FOLDER":
            raise DatabaseError(
                "A folder with this name already exists in this location",
                details={"error_code": "DUPLICATE_FOLDER"},
            )
        raise
    except Exception as e:
        raise DatabaseError("Error creating folder", details={"error": str(e)})


@router.put("/{folder_id}", status_code=200)
async def update_folder(
    folder_id: UUID,
    folder_update: FolderUpdate = Body(...),
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
):
    try:
        result = postgres.update_folder(folder_id, folder_update, str(user["sub"]))
        if result is None:
            raise NotFoundError(
                "Folder not found or unauthorized",
                details={"folder_id": str(folder_id)},
            )
        return success_response(message="Folder updated successfully", data=result)
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError("Error updating folder", details={"error": str(e)})


@router.delete("/{folder_id}", status_code=204)
async def delete_folder(
    folder_id: UUID,
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
):
    try:
        result = postgres.delete_folder(folder_id, str(user["sub"]))
        if result is None:
            raise NotFoundError(
                "Folder not found or unauthorized",
                details={"folder_id": str(folder_id)},
            )
        return success_response(message="Folder deleted successfully", data=None)
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError("Error deleting folder", details={"error": str(e)})
