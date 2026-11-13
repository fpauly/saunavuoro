"""Use cases for managing saunas."""

from __future__ import annotations

from saunavuoro.application.exceptions import ConflictError, EntityNotFoundError
from saunavuoro.application.ports import SaunaRepository
from saunavuoro.domain.entities import Sauna


class CreateSauna:
    def __init__(self, saunas: SaunaRepository) -> None:
        self._saunas = saunas

    def execute(
        self,
        *,
        name: str,
        location: str,
        capacity: int,
        description: str | None = None,
    ) -> Sauna:
        sauna = Sauna(name=name, location=location, capacity=capacity, description=description)
        if self._saunas.exists_by_name(sauna.name):
            raise ConflictError(f"Sauna {sauna.name} already exists.")
        return self._saunas.add(sauna)


class ListSaunas:
    def __init__(self, saunas: SaunaRepository) -> None:
        self._saunas = saunas

    def execute(self) -> list[Sauna]:
        return self._saunas.list()


class GetSauna:
    def __init__(self, saunas: SaunaRepository) -> None:
        self._saunas = saunas

    def execute(self, sauna_id: int) -> Sauna:
        sauna = self._saunas.get(sauna_id)
        if sauna is None:
            raise EntityNotFoundError("Sauna", sauna_id)
        return sauna


class UpdateSauna:
    def __init__(self, saunas: SaunaRepository) -> None:
        self._saunas = saunas

    def execute(
        self,
        sauna_id: int,
        *,
        name: str,
        location: str,
        capacity: int,
        description: str | None = None,
    ) -> Sauna:
        if self._saunas.get(sauna_id) is None:
            raise EntityNotFoundError("Sauna", sauna_id)

        sauna = Sauna(
            name=name,
            location=location,
            capacity=capacity,
            description=description,
            id=sauna_id,
        )
        if self._saunas.exists_by_name(sauna.name, exclude_id=sauna_id):
            raise ConflictError(f"Sauna {sauna.name} already exists.")
        return self._saunas.update(sauna)


class DeleteSauna:
    def __init__(self, saunas: SaunaRepository) -> None:
        self._saunas = saunas

    def execute(self, sauna_id: int) -> None:
        if self._saunas.get(sauna_id) is None:
            raise EntityNotFoundError("Sauna", sauna_id)
        self._saunas.delete(sauna_id)
