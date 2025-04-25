# app/api/endpoints/files.py

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from pydantic import BaseModel

from app.database.supabase_postgres import SupabasePostgres, get_postgres
from app.database.supabase_storage import SupabaseStorage, get_storage
from app.models.file import FileCreate, FileUpdate
from app.utils.auth import verify_jwt
from app.utils.exceptions import DatabaseError, NotFoundError, StorageError
from app.utils.logger import logger
from app.utils.response import success_response

router = APIRouter()


class GetFilesRequest(BaseModel):
    folder_id: Optional[UUID] = None


@router.get("", status_code=200)
async def get_files(
    folder_id: Optional[UUID] = Query(
        None,
        description="Only return files whose folder_id matches this UUID; omit for root-level",
    ),
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
):
    try:
        files = postgres.get_files(str(user["sub"]), folder_id)
        return success_response(message="Files fetched successfully", data=files)
    except Exception as e:
        raise DatabaseError("Error fetching files", details={"error": str(e)})


@router.post("", status_code=201)
async def create_file(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
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
        file_name = name if name else file.filename

        try:
            storage_path = await storage.upload_file(
                file_name,
                file_content,
                UUID(user["sub"]),
                folder_id,
            )
        except StorageError as e:
            raise e
        except Exception as e:
            raise StorageError(
                "Error uploading file to storage", details={"error": str(e)}
            )

        if not storage_path:
            raise StorageError("Failed to get storage path after upload")

        file_data = FileCreate(
            name=file_name,
            storage_path=storage_path,
            folder_id=str(folder_id) if folder_id else None,
        )

        try:
            created_file = postgres.create_file(file_data, str(user["sub"]))
            return success_response(
                message="File created successfully", data=created_file
            )
        except Exception as e:
            # If database creation fails, attempt to clean up the uploaded file
            try:
                await storage.delete_file(storage_path)
            except Exception as cleanup_error:
                logger.error(
                    f"Failed to clean up file after database error: {str(cleanup_error)}"
                )
            raise DatabaseError(
                "Error creating file in database", details={"error": str(e)}
            )
    except (StorageError, DatabaseError):
        raise
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

        file_content = await storage.download_file(file.storage_path)
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

        url = await storage.get_file_url(file.storage_path, expires_in)
        return success_response(
            message="File URL generated successfully", data={"url": url}
        )
    except NotFoundError:
        raise
    except Exception as e:
        raise StorageError("Error generating file URL", details={"error": str(e)})


@router.put("/{file_id}")
async def update_file(
    file_id: UUID,
    name: Optional[str] = Form(None),
    folder_id: Optional[UUID] = Form(None),
    file_content: Optional[UploadFile] = File(None),
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
    storage: SupabaseStorage = Depends(get_storage),
):
    try:
        existing_file = postgres.get_file(file_id, str(user["sub"]))
        if not existing_file:
            raise NotFoundError(
                "File not found or unauthorized", details={"file_id": str(file_id)}
            )

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if folder_id is not None:
            update_data["folder_id"] = str(folder_id)

        if file_content:
            if not file_content.filename.lower().endswith(".tex"):
                raise StorageError(
                    "Invalid file type",
                    details={"error": "Only .tex files are allowed"},
                )

            content = await file_content.read()
            new_name = name if name else existing_file.name

            await storage.upload_file(
                new_name,
                content,
                UUID(user["sub"]),
                folder_id if folder_id else existing_file.folder_id,
            )

        result = postgres.update_file(
            file_id, FileUpdate(**update_data), str(user["sub"])
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

        await storage.delete_file(file.storage_path)
        postgres.delete_file(file_id, str(user["sub"]))
        return success_response(message="File deleted successfully", data=None)
    except NotFoundError:
        raise
    except Exception as e:
        raise StorageError("Error deleting file", details={"error": str(e)})
