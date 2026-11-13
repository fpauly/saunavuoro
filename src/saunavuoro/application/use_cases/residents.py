"""Resident use cases. One class per use case, each with an execute() method."""

from uuid import UUID

from saunavuoro.application.errors import NotFoundError
from saunavuoro.application.ports import UnitOfWork
from saunavuoro.domain.resident import Resident


class CreateResident:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, apartment_id: UUID, name: str) -> Resident:
        resident = Resident(apartment_id=apartment_id, name=name)
        with self._uow as uow:
            if uow.apartments.get(apartment_id) is None:
                raise NotFoundError("Apartment", apartment_id)
            uow.residents.add(resident)
            uow.commit()
        return resident


class GetResident:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, resident_id: UUID) -> Resident:
        with self._uow as uow:
            resident = uow.residents.get(resident_id)
        if resident is None:
            raise NotFoundError("Resident", resident_id)
        return resident


class ListResidents:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, apartment_id: UUID | None = None) -> list[Resident]:
        with self._uow as uow:
            if apartment_id is not None:
                return uow.residents.list_by_apartment(apartment_id)
            return uow.residents.list_all()


class UpdateResident:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, resident_id: UUID, apartment_id: UUID, name: str) -> Resident:
        with self._uow as uow:
            if uow.residents.get(resident_id) is None:
                raise NotFoundError("Resident", resident_id)
            if uow.apartments.get(apartment_id) is None:
                raise NotFoundError("Apartment", apartment_id)
            resident = Resident(id=resident_id, apartment_id=apartment_id, name=name)
            uow.residents.update(resident)
            uow.commit()
        return resident


class DeleteResident:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, resident_id: UUID) -> None:
        with self._uow as uow:
            if uow.residents.get(resident_id) is None:
                raise NotFoundError("Resident", resident_id)
            uow.residents.delete(resident_id)
            uow.commit()
