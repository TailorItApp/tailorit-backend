# backend/app/api/v1/router.py

from fastapi import APIRouter

from app.api.endpoints import test

api_router = APIRouter()
api_router.include_router(test.router, tags=["test"])
