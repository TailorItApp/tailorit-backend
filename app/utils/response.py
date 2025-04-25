# app/utils/response.py

from typing import Any, Optional

from pydantic import BaseModel, Field


class StandardResponse(BaseModel):
    status: bool = Field(..., description="Indicates success (true) or failure (false)")
    message: Optional[str] = Field(
        None, description="A descriptive message about the response"
    )
    data: Optional[Any] = Field(
        None, description="The payload data for success responses"
    )


def success_response(
    message: str = "Success",
    data: Optional[Any] = None,
) -> StandardResponse:
    return StandardResponse(status=True, message=message, data=data)


def error_response(
    message: str = "An error occurred",
    data: Optional[Any] = None,
) -> StandardResponse:
    return StandardResponse(status=False, message=message, data=data)
