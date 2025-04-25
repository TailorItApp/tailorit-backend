# app/api/endpoints/files.py

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, File, Form, UploadFile
from pydantic import BaseModel

from app.database.supabase_postgres import SupabasePostgres, get_postgres
from app.database.supabase_storage import SupabaseStorage, get_storage
from app.models.file import FileCreate, FileModel, FileUpdate
from app.utils.auth import verify_jwt
from app.utils.exceptions import DatabaseError, NotFoundError, StorageError
from app.utils.response import success_response

router = APIRouter()


class GetFilesRequest(BaseModel):
    folder_id: Optional[UUID] = None


@router.get("", status_code=200)
async def get_files(
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
):
    try:
        files = postgres.get_files(str(user["sub"]))
        return success_response(message="Files fetched successfully", data=files)
    except Exception as e:
        raise DatabaseError("Error fetching files", details={"error": str(e)})


@router.post("", status_code=201)
async def create_file(
    file: UploadFile = File(...),
    folder_id: Optional[UUID] = Form(None),
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        if not file.filename.lower().endswith(".tex"):
            raise StorageError(
                "Invalid file type", details={"error": "Only .tex files are allowed"}
            )

        file_content = await file.read()

        storage_path = await storage.upload_file(
            file.filename,
            file_content,
            UUID(user["sub"]),
            folder_id,
        )

        file_data = FileCreate(
            name=file.filename,
            storage_path=storage_path,
            folder_id=str(folder_id) if folder_id else None,
        )

        created_file = postgres.create_file(file_data, str(user["sub"]))
        return success_response(message="File created successfully", data=created_file)
    except Exception as e:
        raise StorageError("Error processing file", details={"error": str(e)})


@router.get("/{file_id}/download")
async def download_file(
    file_id: UUID,
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        file = postgres.get_file(file_id, str(user["sub"]))
        if not file:
            raise NotFoundError(
                "File not found or unauthorized", details={"file_id": str(file_id)}
            )

        file_content = await storage.download_file(file["storage_path"])
        return success_response(
            message="File downloaded successfully", data={"content": file_content}
        )
    except NotFoundError:
        raise
    except Exception as e:
        raise StorageError("Error downloading file", details={"error": str(e)})


@router.get("/{file_id}/url")
async def get_file_url(
    file_id: UUID,
    expires_in: int = 3600,
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        file = postgres.get_file(file_id, str(user["sub"]))
        if not file:
            raise NotFoundError(
                "File not found or unauthorized", details={"file_id": str(file_id)}
            )

        url = await storage.get_file_url(file["storage_path"], expires_in)
        return success_response(
            message="File URL generated successfully", data={"url": url}
        )
    except NotFoundError:
        raise
    except Exception as e:
        raise StorageError("Error generating file URL", details={"error": str(e)})


@router.put("/{file_id}", response_model=FileModel)
async def update_file(
    file_id: UUID,
    file_update: FileUpdate = Body(...),
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
):
    try:
        update_data = file_update.model_dump(exclude_unset=True)
        result = postgres.update_file(file_id, update_data, str(user["sub"]))
        if result is None:
            raise NotFoundError(
                "File not found or unauthorized", details={"file_id": str(file_id)}
            )
        return success_response(message="File updated successfully", data=result)
    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError("Error updating file", details={"error": str(e)})


@router.delete("/{file_id}", status_code=204)
async def delete_file(
    file_id: UUID,
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        file = postgres.get_file(file_id, str(user["sub"]))
        if not file:
            raise NotFoundError(
                "File not found or unauthorized", details={"file_id": str(file_id)}
            )

        await storage.delete_file(file["storage_path"])
        postgres.delete_file(file_id, str(user["sub"]))
        return success_response(message="File deleted successfully", data=None)
    except NotFoundError:
        raise
    except Exception as e:
        raise StorageError("Error deleting file", details={"error": str(e)})
