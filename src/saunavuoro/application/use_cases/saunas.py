"""Sauna use cases. One class per use case, each with an execute() method."""

from datetime import time
from uuid import UUID

from saunavuoro.application.errors import NotFoundError
from saunavuoro.application.ports import UnitOfWork
from saunavuoro.domain.sauna import Sauna


class CreateSauna:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(
        self,
        name: str,
        opens_at: time,
        closes_at: time,
        turn_length_minutes: int = 60,
        max_extra_bookings_per_week: int = 1,
        max_days_ahead: int = 14,
        cancellation_deadline_hours: int = 2,
    ) -> Sauna:
        sauna = Sauna(
            name=name,
            opens_at=opens_at,
            closes_at=closes_at,
            turn_length_minutes=turn_length_minutes,
            max_extra_bookings_per_week=max_extra_bookings_per_week,
            max_days_ahead=max_days_ahead,
            cancellation_deadline_hours=cancellation_deadline_hours,
        )
        with self._uow as uow:
            uow.saunas.add(sauna)
            uow.commit()
        return sauna


class GetSauna:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, sauna_id: UUID) -> Sauna:
        with self._uow as uow:
            sauna = uow.saunas.get(sauna_id)
        if sauna is None:
            raise NotFoundError("Sauna", sauna_id)
        return sauna


class ListSaunas:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self) -> list[Sauna]:
        with self._uow as uow:
            return uow.saunas.list_all()


class UpdateSauna:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(
        self,
        sauna_id: UUID,
        name: str,
        opens_at: time,
        closes_at: time,
        turn_length_minutes: int = 60,
        max_extra_bookings_per_week: int = 1,
        max_days_ahead: int = 14,
        cancellation_deadline_hours: int = 2,
    ) -> Sauna:
        with self._uow as uow:
            if uow.saunas.get(sauna_id) is None:
                raise NotFoundError("Sauna", sauna_id)
            sauna = Sauna(
                id=sauna_id,
                name=name,
                opens_at=opens_at,
                closes_at=closes_at,
                turn_length_minutes=turn_length_minutes,
                max_extra_bookings_per_week=max_extra_bookings_per_week,
                max_days_ahead=max_days_ahead,
                cancellation_deadline_hours=cancellation_deadline_hours,
            )
            uow.saunas.update(sauna)
            uow.commit()
        return sauna


class DeleteSauna:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, sauna_id: UUID) -> None:
        with self._uow as uow:
            if uow.saunas.get(sauna_id) is None:
                raise NotFoundError("Sauna", sauna_id)
            uow.saunas.delete(sauna_id)
            uow.commit()
