# app/utils/exception_handlers.py


from fastapi import Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from app.utils.exceptions import BaseAPIException
from app.utils.logger import logger
from app.utils.response import error_response


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation Error in {request.url.path}: {str(exc)}")

    error_details = {
        "type": "ValidationError",
        "errors": exc.errors(),
    }

    response = error_response(
        message="Validation error",
        data={
            "error_code": "VALIDATION_ERROR",
            "details": error_details,
        },
    )

    return JSONResponse(status_code=422, content=response.dict())


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Error in {request.url.path}: {str(exc)}")

    error_details = {
        "type": "HTTPException",
        "status_code": exc.status_code,
        "detail": exc.detail,
    }

    response = error_response(
        message=str(exc.detail),
        data={
            "error_code": f"HTTP_{exc.status_code}",
            "details": error_details,
        },
    )

    return JSONResponse(status_code=exc.status_code, content=response.dict())


async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, BaseAPIException):
        logger.error(f"API Error in {request.url.path}: {str(exc)}")
        error_details = exc.details
        status_code = exc.status_code
        error_code = exc.error_code
        message = exc.message
    else:
        logger.error(f"Unexpected Error in {request.url.path}: {str(exc)}")
        error_details = {
            "type": exc.__class__.__name__,
        }
        status_code = 500
        error_code = "INTERNAL_SERVER_ERROR"
        message = "An unexpected error occurred"

    response = error_response(
        message=message,
        data={
            "error_code": error_code,
            "details": error_details,
        },
    )

    return JSONResponse(status_code=status_code, content=response.dict())


def register_exception_handlers(app):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
