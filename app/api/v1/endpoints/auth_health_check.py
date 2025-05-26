# app/api/endpoints/auth_health_check.py


from fastapi import APIRouter, Depends

from app.utils.auth import verify_jwt
from app.utils.response import error_response, success_response

router = APIRouter()


@router.get("/", status_code=200)
async def auth_health_check(
    user: dict = Depends(verify_jwt),
):
    try:
        return success_response(message="Auth health check successful", data=user)
    except Exception as e:
        return error_response(message="Auth health check failed", data=e)
