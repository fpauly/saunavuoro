"""Use cases for managing apartments."""

from __future__ import annotations

from saunavuoro.application.exceptions import ConflictError, EntityNotFoundError
from saunavuoro.application.ports import ApartmentRepository, ResidentRepository
from saunavuoro.domain.entities import Apartment


class CreateApartment:
    def __init__(self, apartments: ApartmentRepository) -> None:
        self._apartments = apartments

    def execute(self, *, number: str, floor: int) -> Apartment:
        apartment = Apartment(number=number, floor=floor)
        if self._apartments.exists_by_number(apartment.number):
            raise ConflictError(f"Apartment {apartment.number} already exists.")
        return self._apartments.add(apartment)


class ListApartments:
    def __init__(self, apartments: ApartmentRepository) -> None:
        self._apartments = apartments

    def execute(self) -> list[Apartment]:
        return self._apartments.list()


class GetApartment:
    def __init__(self, apartments: ApartmentRepository) -> None:
        self._apartments = apartments

    def execute(self, apartment_id: int) -> Apartment:
        apartment = self._apartments.get(apartment_id)
        if apartment is None:
            raise EntityNotFoundError("Apartment", apartment_id)
        return apartment


class UpdateApartment:
    def __init__(self, apartments: ApartmentRepository) -> None:
        self._apartments = apartments

    def execute(self, apartment_id: int, *, number: str, floor: int) -> Apartment:
        if self._apartments.get(apartment_id) is None:
            raise EntityNotFoundError("Apartment", apartment_id)

        apartment = Apartment(number=number, floor=floor, id=apartment_id)
        if self._apartments.exists_by_number(apartment.number, exclude_id=apartment_id):
            raise ConflictError(f"Apartment {apartment.number} already exists.")
        return self._apartments.update(apartment)


class DeleteApartment:
    def __init__(
        self,
        apartments: ApartmentRepository,
        residents: ResidentRepository,
    ) -> None:
        self._apartments = apartments
        self._residents = residents

    def execute(self, apartment_id: int) -> None:
        if self._apartments.get(apartment_id) is None:
            raise EntityNotFoundError("Apartment", apartment_id)
        if self._residents.count_by_apartment(apartment_id) > 0:
            raise ConflictError(
                "Apartment cannot be deleted while it has residents. "
                "Move or delete the residents first."
            )
        self._apartments.delete(apartment_id)
