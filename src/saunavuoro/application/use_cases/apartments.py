"""Apartment use cases. One class per use case, each with an execute() method."""

from uuid import UUID

from saunavuoro.application.errors import AlreadyExistsError, NotFoundError
from saunavuoro.application.ports import UnitOfWork
from saunavuoro.domain.apartment import Apartment


class CreateApartment:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, number: str) -> Apartment:
        apartment = Apartment(number=number)  # domain validates the number
        with self._uow as uow:
            if uow.apartments.get_by_number(apartment.number) is not None:
                raise AlreadyExistsError(f"Apartment {apartment.number} already exists.")
            uow.apartments.add(apartment)
            uow.commit()
        return apartment


class GetApartment:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, apartment_id: UUID) -> Apartment:
        with self._uow as uow:
            apartment = uow.apartments.get(apartment_id)
        if apartment is None:
            raise NotFoundError("Apartment", apartment_id)
        return apartment


class ListApartments:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self) -> list[Apartment]:
        with self._uow as uow:
            return uow.apartments.list_all()


class UpdateApartment:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, apartment_id: UUID, number: str) -> Apartment:
        with self._uow as uow:
            if uow.apartments.get(apartment_id) is None:
                raise NotFoundError("Apartment", apartment_id)
            apartment = Apartment(id=apartment_id, number=number)  # domain validates
            other = uow.apartments.get_by_number(apartment.number)
            if other is not None and other.id != apartment.id:
                raise AlreadyExistsError(f"Apartment {apartment.number} already exists.")
            uow.apartments.update(apartment)
            uow.commit()
        return apartment


class DeleteApartment:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, apartment_id: UUID) -> None:
        with self._uow as uow:
            if uow.apartments.get(apartment_id) is None:
                raise NotFoundError("Apartment", apartment_id)
            uow.apartments.delete(apartment_id)
            uow.commit()
