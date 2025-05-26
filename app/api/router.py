# app/api/router.py

from fastapi import APIRouter

from app.api.endpoints import auth_health_check, files, filesystem, folders

api_router = APIRouter()
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(folders.router, prefix="/folders", tags=["folders"])
api_router.include_router(filesystem.router, prefix="/filesystem", tags=["filesystem"])
api_router.include_router(
    auth_health_check.router, prefix="/auth_health_check", tags=["auth_health_check"]
)
