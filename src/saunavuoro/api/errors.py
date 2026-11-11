"""Translate domain and application errors into HTTP responses."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from saunavuoro.api.schemas.errors import ErrorResponse
from saunavuoro.application.errors import (
    AlreadyExistsError,
    ApplicationError,
    ConflictError,
    NotFoundError,
)
from saunavuoro.domain.errors import DomainError

_STATUS_BY_ERROR: dict[type[Exception], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    AlreadyExistsError: status.HTTP_409_CONFLICT,
    ConflictError: status.HTTP_409_CONFLICT,
}


async def _handle(request: Request, exc: Exception) -> JSONResponse:
    # Unmapped domain errors are broken business rules -> 422.
    code = _STATUS_BY_ERROR.get(type(exc), status.HTTP_422_UNPROCESSABLE_CONTENT)
    return JSONResponse(status_code=code, content=ErrorResponse(detail=str(exc)).model_dump())


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, _handle)
    app.add_exception_handler(DomainError, _handle)
