"""REST endpoints for resident administration."""

from __future__ import annotations

from fastapi import APIRouter, Query, Response, status

from saunavuoro.api.dependencies import SessionDep
from saunavuoro.api.schemas import ResidentCreate, ResidentResponse, ResidentUpdate
from saunavuoro.application.residents import (
    CreateResident,
    DeleteResident,
    GetResident,
    ListResidents,
    UpdateResident,
)
from saunavuoro.infrastructure.repositories import (
    SqlAlchemyApartmentRepository,
    SqlAlchemyResidentRepository,
)

router = APIRouter(prefix="/residents", tags=["residents"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ResidentResponse)
def create_resident(payload: ResidentCreate, session: SessionDep) -> ResidentResponse:
    resident = CreateResident(
        SqlAlchemyResidentRepository(session),
        SqlAlchemyApartmentRepository(session),
    ).execute(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        apartment_id=payload.apartment_id,
        phone=payload.phone,
    )
    session.commit()
    return ResidentResponse.model_validate(resident)


@router.get("", response_model=list[ResidentResponse])
def list_residents(
    session: SessionDep,
    apartment_id: int | None = Query(default=None, ge=1),
) -> list[ResidentResponse]:
    residents = ListResidents(SqlAlchemyResidentRepository(session)).execute(apartment_id)
    return [ResidentResponse.model_validate(resident) for resident in residents]


@router.get("/{resident_id}", response_model=ResidentResponse)
def get_resident(resident_id: int, session: SessionDep) -> ResidentResponse:
    resident = GetResident(SqlAlchemyResidentRepository(session)).execute(resident_id)
    return ResidentResponse.model_validate(resident)


@router.put("/{resident_id}", response_model=ResidentResponse)
def update_resident(
    resident_id: int,
    payload: ResidentUpdate,
    session: SessionDep,
) -> ResidentResponse:
    resident = UpdateResident(
        SqlAlchemyResidentRepository(session),
        SqlAlchemyApartmentRepository(session),
    ).execute(
        resident_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        apartment_id=payload.apartment_id,
        phone=payload.phone,
    )
    session.commit()
    return ResidentResponse.model_validate(resident)


@router.delete("/{resident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resident(resident_id: int, session: SessionDep) -> Response:
    DeleteResident(SqlAlchemyResidentRepository(session)).execute(resident_id)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
