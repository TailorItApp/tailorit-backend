from fastapi import APIRouter, Depends

from app.database.supabase_postgres import SupabasePostgres, get_postgres
from app.utils.auth import verify_jwt
from app.utils.exceptions import DatabaseError
from app.utils.response import success_response

router = APIRouter()


@router.get("", status_code=200)
async def get_filesystem(
    user: dict = Depends(verify_jwt),
    postgres: SupabasePostgres = Depends(get_postgres),
):
    try:
        folders = postgres.get_all_folders_recursive(str(user["sub"]))
        files = postgres.get_files(str(user["sub"]))
        filesystem = {"folders": folders, "files": files}
        return success_response(
            message="Filesystem fetched successfully", data=filesystem
        )
    except Exception as e:
        raise DatabaseError("Error fetching filesystem", details={"error": str(e)})
