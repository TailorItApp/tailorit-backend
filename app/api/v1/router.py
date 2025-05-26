# app/api/router.py

from fastapi import APIRouter

from app.api.v1.endpoints import auth_health_check, filesystem

api_router = APIRouter()

api_router.include_router(
    auth_health_check.router, prefix="/auth_health_check", tags=["auth_health_check"]
)
api_router.include_router(filesystem.router, prefix="/filesystem", tags=["filesystem"])
