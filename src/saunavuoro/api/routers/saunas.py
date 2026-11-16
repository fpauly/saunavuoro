"""/saunas endpoints. Routers only convert data and call use cases (no business logic).

The docstring of each endpoint is shown as its description in Swagger UI.
"""

from uuid import UUID

from fastapi import APIRouter, status

from saunavuoro.api.dependencies import Uow
from saunavuoro.api.schemas.errors import error_responses
from saunavuoro.api.schemas.saunas import SaunaIn, SaunaOut
from saunavuoro.application.use_cases.saunas import (
    CreateSauna,
    DeleteSauna,
    GetSauna,
    ListSaunas,
    UpdateSauna,
)

router = APIRouter(prefix="/saunas", tags=["saunas"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a sauna",
    responses=error_responses(422),
)
def create_sauna(body: SaunaIn, uow: Uow) -> SaunaOut:
    """Add a new sauna with its opening hours and booking rules."""
    sauna = CreateSauna(uow).execute(
        body.name,
        body.opens_at,
        body.closes_at,
        body.turn_length_minutes,
        body.max_extra_bookings_per_week,
        body.max_days_ahead,
        body.cancellation_deadline_hours,
    )
    return SaunaOut.from_entity(sauna)


@router.get("", summary="List saunas")
def list_saunas(uow: Uow) -> list[SaunaOut]:
    """Return all saunas, sorted by name."""
    return [SaunaOut.from_entity(s) for s in ListSaunas(uow).execute()]


@router.get(
    "/{sauna_id}",
    summary="Get a sauna",
    responses=error_responses(404, 422),
)
def get_sauna(sauna_id: UUID, uow: Uow) -> SaunaOut:
    """Return one sauna by id."""
    return SaunaOut.from_entity(GetSauna(uow).execute(sauna_id))


@router.put(
    "/{sauna_id}",
    summary="Update a sauna",
    responses=error_responses(404, 422),
)
def update_sauna(sauna_id: UUID, body: SaunaIn, uow: Uow) -> SaunaOut:
    """Change the sauna's name, opening hours or booking rules."""
    sauna = UpdateSauna(uow).execute(
        sauna_id,
        body.name,
        body.opens_at,
        body.closes_at,
        body.turn_length_minutes,
        body.max_extra_bookings_per_week,
        body.max_days_ahead,
        body.cancellation_deadline_hours,
    )
    return SaunaOut.from_entity(sauna)


@router.delete(
    "/{sauna_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a sauna",
    responses=error_responses(404, 409, 422),
)
def delete_sauna(sauna_id: UUID, uow: Uow) -> None:
    """Remove a sauna. A sauna with weekly turns or bookings cannot be deleted."""
    DeleteSauna(uow).execute(sauna_id)
