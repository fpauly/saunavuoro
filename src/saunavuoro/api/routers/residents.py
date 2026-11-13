"""/residents endpoints. Routers only convert data and call use cases (no business logic).

The docstring of each endpoint is shown as its description in Swagger UI.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from saunavuoro.api.dependencies import Uow
from saunavuoro.api.schemas.errors import error_responses
from saunavuoro.api.schemas.residents import ResidentIn, ResidentOut
from saunavuoro.application.use_cases.residents import (
    CreateResident,
    DeleteResident,
    GetResident,
    ListResidents,
    UpdateResident,
)

router = APIRouter(prefix="/residents", tags=["residents"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a resident",
    responses=error_responses(404, 422),
)
def create_resident(body: ResidentIn, uow: Uow) -> ResidentOut:
    """Add a resident to an existing apartment."""
    resident = CreateResident(uow).execute(body.apartment_id, body.name)
    return ResidentOut.from_entity(resident)


@router.get("", summary="List residents")
def list_residents(
    uow: Uow,
    apartment_id: Annotated[
        UUID | None,
        Query(description="Return only the residents of this apartment."),
    ] = None,
) -> list[ResidentOut]:
    """Return all residents, or the residents of one apartment."""
    return [ResidentOut.from_entity(r) for r in ListResidents(uow).execute(apartment_id)]


@router.get(
    "/{resident_id}",
    summary="Get a resident",
    responses=error_responses(404, 422),
)
def get_resident(resident_id: UUID, uow: Uow) -> ResidentOut:
    """Return one resident by id."""
    return ResidentOut.from_entity(GetResident(uow).execute(resident_id))


@router.put(
    "/{resident_id}",
    summary="Update a resident",
    responses=error_responses(404, 422),
)
def update_resident(resident_id: UUID, body: ResidentIn, uow: Uow) -> ResidentOut:
    """Change the resident's name or move them to another apartment."""
    resident = UpdateResident(uow).execute(resident_id, body.apartment_id, body.name)
    return ResidentOut.from_entity(resident)


@router.delete(
    "/{resident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resident",
    responses=error_responses(404, 422),
)
def delete_resident(resident_id: UUID, uow: Uow) -> None:
    """Remove a resident from the building."""
    DeleteResident(uow).execute(resident_id)
