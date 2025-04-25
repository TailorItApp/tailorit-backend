# app/api/router.py

from fastapi import APIRouter

from app.api.endpoints import files, folders, test

api_router = APIRouter()
api_router.include_router(test.router, tags=["test"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(folders.router, prefix="/folders", tags=["folders"])
