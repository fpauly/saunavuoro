"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from saunavuoro.api.dependencies import DatabaseDep
from saunavuoro.api.errors import register_exception_handlers
from saunavuoro.api.routers import api_router
from saunavuoro.infrastructure.config import get_settings

API_VERSION = "0.1.0"


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=API_VERSION,
        description=(
            "REST API for managing apartments, residents and saunas in a Finnish "
            "apartment building. Admin operations are exposed without authentication "
            "in this course project."
        ),
    )
    app.include_router(api_router, prefix=settings.api_prefix)
    register_exception_handlers(app)

    @app.get("/", tags=["health"], include_in_schema=False)
    def root() -> dict[str, str]:
        return {
            "name": settings.app_name,
            "docs": "/docs",
            "health": "/health",
        }

    @app.get("/health", tags=["health"])
    def health(database: DatabaseDep) -> JSONResponse:
        if not database.is_reachable():
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "unavailable", "database": "unreachable"},
            )
        return JSONResponse(content={"status": "ok", "database": "reachable"})

    return app


app = create_app()
