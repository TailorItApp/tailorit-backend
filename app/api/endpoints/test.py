# backend/app/api/v1/endpoints/chat.py


from fastapi import APIRouter, Response
from fastapi import Request as ServerRequest

from app.utils.logger import logger
from app.utils.response import success_response

router = APIRouter()


@router.get("/test")
async def chat(request: ServerRequest, response: Response):
    logger.info("Test endpoint")
    return success_response(message="Test endpoint")
