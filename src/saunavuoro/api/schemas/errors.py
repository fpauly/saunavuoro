"""Error response models, used in the OpenAPI documentation of every router."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Returned when a use case or a business rule rejects the request."""

    detail: str = Field(examples=["Apartment A 1 already exists."])


class ValidationIssue(BaseModel):
    loc: list[str | int] = Field(examples=[["body", "number"]])
    msg: str = Field(examples=["Field required"])
    type: str = Field(examples=["missing"])


class ValidationErrorResponse(BaseModel):
    """Returned by FastAPI when the request body or parameters are invalid."""

    detail: list[ValidationIssue]


_RESPONSES: dict[int, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "The resource was not found."},
    409: {"model": ErrorResponse, "description": "Conflicts with existing data."},
    422: {
        "model": ErrorResponse | ValidationErrorResponse,
        "description": "Invalid request data, or a business rule was broken.",
    },
}


def error_responses(*status_codes: int) -> dict[int | str, dict[str, Any]]:
    """Use in a route: `@router.post(..., responses=error_responses(409, 422))`."""
    return {code: _RESPONSES[code] for code in status_codes}
