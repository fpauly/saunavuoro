from fastapi import FastAPI

from saunavuoro.api.dependencies import UnitOfWorkFactory
from saunavuoro.api.errors import register_error_handlers
from saunavuoro.api.routers import apartments, bookings, residents, saunas, weekly_turns
from saunavuoro.application.ports import Clock

DESCRIPTION = """
REST API for booking sauna turns in a Finnish apartment building.

* Interactive documentation (Swagger UI): `/docs`
* Alternative documentation (ReDoc): `/redoc`
* OpenAPI specification: `/openapi.json`

All errors return JSON with a `detail` field.
"""

TAGS = [
    {"name": "apartments", "description": "Apartments of the building (administrator)."},
    {"name": "residents", "description": "Residents living in the apartments."},
    {"name": "saunas", "description": "Saunas, opening hours and booking rules (administrator)."},
    {"name": "weekly-turns", "description": "Fixed weekly sauna turns of the apartments."},
    {"name": "bookings", "description": "One-off bookings of free sauna turns."},
]


def create_app(uow_factory: UnitOfWorkFactory, clock: Clock) -> FastAPI:
    app = FastAPI(
        title="SaunaVuoro API",
        description=DESCRIPTION,
        version="0.1.0",
        openapi_tags=TAGS,
    )
    app.state.uow_factory = uow_factory
    app.state.clock = clock
    register_error_handlers(app)
    for module in (apartments, residents, saunas, weekly_turns, bookings):
        app.include_router(module.router, prefix="/api/v1")
    return app
