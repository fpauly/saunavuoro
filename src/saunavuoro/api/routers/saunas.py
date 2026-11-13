"""REST endpoints for sauna administration."""

from __future__ import annotations

from fastapi import APIRouter, Response, status

from saunavuoro.api.dependencies import SessionDep
from saunavuoro.api.schemas import SaunaCreate, SaunaResponse, SaunaUpdate
from saunavuoro.application.saunas import (
    CreateSauna,
    DeleteSauna,
    GetSauna,
    ListSaunas,
    UpdateSauna,
)
from saunavuoro.infrastructure.repositories import SqlAlchemySaunaRepository

router = APIRouter(prefix="/saunas", tags=["saunas"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=SaunaResponse)
def create_sauna(payload: SaunaCreate, session: SessionDep) -> SaunaResponse:
    sauna = CreateSauna(SqlAlchemySaunaRepository(session)).execute(
        name=payload.name,
        location=payload.location,
        capacity=payload.capacity,
        description=payload.description,
    )
    session.commit()
    return SaunaResponse.model_validate(sauna)


@router.get("", response_model=list[SaunaResponse])
def list_saunas(session: SessionDep) -> list[SaunaResponse]:
    saunas = ListSaunas(SqlAlchemySaunaRepository(session)).execute()
    return [SaunaResponse.model_validate(sauna) for sauna in saunas]


@router.get("/{sauna_id}", response_model=SaunaResponse)
def get_sauna(sauna_id: int, session: SessionDep) -> SaunaResponse:
    sauna = GetSauna(SqlAlchemySaunaRepository(session)).execute(sauna_id)
    return SaunaResponse.model_validate(sauna)


@router.put("/{sauna_id}", response_model=SaunaResponse)
def update_sauna(
    sauna_id: int,
    payload: SaunaUpdate,
    session: SessionDep,
) -> SaunaResponse:
    sauna = UpdateSauna(SqlAlchemySaunaRepository(session)).execute(
        sauna_id,
        name=payload.name,
        location=payload.location,
        capacity=payload.capacity,
        description=payload.description,
    )
    session.commit()
    return SaunaResponse.model_validate(sauna)


@router.delete("/{sauna_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sauna(sauna_id: int, session: SessionDep) -> Response:
    DeleteSauna(SqlAlchemySaunaRepository(session)).execute(sauna_id)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
