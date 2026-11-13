"""REST endpoints for apartment administration."""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from saunavuoro.api.dependencies import SessionDep
from saunavuoro.api.schemas import ApartmentCreate, ApartmentResponse, ApartmentUpdate
from saunavuoro.application.apartments import (
    CreateApartment,
    DeleteApartment,
    GetApartment,
    ListApartments,
    UpdateApartment,
)
from saunavuoro.infrastructure.repositories import (
    SqlAlchemyApartmentRepository,
    SqlAlchemyResidentRepository,
)

router = APIRouter(prefix="/apartments", tags=["apartments"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ApartmentResponse)
def create_apartment(payload: ApartmentCreate, session: SessionDep) -> ApartmentResponse:
    apartment = CreateApartment(SqlAlchemyApartmentRepository(session)).execute(
        number=payload.number,
        floor=payload.floor,
    )
    session.commit()
    return ApartmentResponse.model_validate(apartment)


@router.get("", response_model=list[ApartmentResponse])
def list_apartments(session: SessionDep) -> list[ApartmentResponse]:
    apartments = ListApartments(SqlAlchemyApartmentRepository(session)).execute()
    return [ApartmentResponse.model_validate(apartment) for apartment in apartments]


@router.get("/{apartment_id}", response_model=ApartmentResponse)
def get_apartment(apartment_id: int, session: SessionDep) -> ApartmentResponse:
    apartment = GetApartment(SqlAlchemyApartmentRepository(session)).execute(apartment_id)
    return ApartmentResponse.model_validate(apartment)


@router.put("/{apartment_id}", response_model=ApartmentResponse)
def update_apartment(
    apartment_id: int,
    payload: ApartmentUpdate,
    session: SessionDep,
) -> ApartmentResponse:
    apartment = UpdateApartment(SqlAlchemyApartmentRepository(session)).execute(
        apartment_id,
        number=payload.number,
        floor=payload.floor,
    )
    session.commit()
    return ApartmentResponse.model_validate(apartment)


@router.delete("/{apartment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_apartment(apartment_id: int, session: SessionDep) -> Response:
    DeleteApartment(
        SqlAlchemyApartmentRepository(session),
        SqlAlchemyResidentRepository(session),
    ).execute(apartment_id)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
