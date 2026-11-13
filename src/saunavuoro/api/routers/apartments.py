"""/apartments endpoints. Routers only convert data and call use cases (no business logic).

The docstring of each endpoint is shown as its description in Swagger UI.
"""

from uuid import UUID

from fastapi import APIRouter, status

from saunavuoro.api.dependencies import Uow
from saunavuoro.api.schemas.apartments import ApartmentIn, ApartmentOut
from saunavuoro.api.schemas.errors import error_responses
from saunavuoro.application.use_cases.apartments import (
    CreateApartment,
    DeleteApartment,
    GetApartment,
    ListApartments,
    UpdateApartment,
)

router = APIRouter(prefix="/apartments", tags=["apartments"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create an apartment",
    responses=error_responses(409, 422),
)
def create_apartment(body: ApartmentIn, uow: Uow) -> ApartmentOut:
    """Add a new apartment to the building. Apartment numbers must be unique."""
    return ApartmentOut.from_entity(CreateApartment(uow).execute(body.number))


@router.get("", summary="List apartments")
def list_apartments(uow: Uow) -> list[ApartmentOut]:
    """Return all apartments, sorted by number."""
    return [ApartmentOut.from_entity(a) for a in ListApartments(uow).execute()]


@router.get(
    "/{apartment_id}",
    summary="Get an apartment",
    responses=error_responses(404, 422),
)
def get_apartment(apartment_id: UUID, uow: Uow) -> ApartmentOut:
    """Return one apartment by its id."""
    return ApartmentOut.from_entity(GetApartment(uow).execute(apartment_id))


@router.put(
    "/{apartment_id}",
    summary="Update an apartment",
    responses=error_responses(404, 409, 422),
)
def update_apartment(apartment_id: UUID, body: ApartmentIn, uow: Uow) -> ApartmentOut:
    """Change the apartment number. The new number must not belong to another apartment."""
    return ApartmentOut.from_entity(UpdateApartment(uow).execute(apartment_id, body.number))


@router.delete(
    "/{apartment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an apartment",
    responses=error_responses(404, 422),
)
def delete_apartment(apartment_id: UUID, uow: Uow) -> None:
    """Remove an apartment from the building."""
    DeleteApartment(uow).execute(apartment_id)
