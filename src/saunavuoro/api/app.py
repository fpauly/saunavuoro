from fastapi import FastAPI

from saunavuoro.api.dependencies import UnitOfWorkFactory
from saunavuoro.api.errors import register_error_handlers
from saunavuoro.api.routers import apartments

DESCRIPTION = """
REST API for booking sauna turns in a Finnish apartment building.

* Interactive documentation (Swagger UI): `/docs`
* Alternative documentation (ReDoc): `/redoc`
* OpenAPI specification: `/openapi.json`

All errors return JSON with a `detail` field.
"""

TAGS = [
    {"name": "apartments", "description": "Apartments of the building (administrator)."},
]


def create_app(uow_factory: UnitOfWorkFactory) -> FastAPI:
    app = FastAPI(
        title="SaunaVuoro API",
        description=DESCRIPTION,
        version="0.1.0",
        openapi_tags=TAGS,
    )
    app.state.uow_factory = uow_factory
    register_error_handlers(app)
    app.include_router(apartments.router, prefix="/api/v1")
    return app
