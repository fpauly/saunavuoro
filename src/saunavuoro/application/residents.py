"""Use cases for managing residents."""

from __future__ import annotations

from saunavuoro.application.exceptions import ConflictError, EntityNotFoundError
from saunavuoro.application.ports import ApartmentRepository, ResidentRepository
from saunavuoro.domain.entities import Resident


class CreateResident:
    def __init__(
        self,
        residents: ResidentRepository,
        apartments: ApartmentRepository,
    ) -> None:
        self._residents = residents
        self._apartments = apartments

    def execute(
        self,
        *,
        first_name: str,
        last_name: str,
        email: str,
        apartment_id: int,
        phone: str | None = None,
    ) -> Resident:
        if self._apartments.get(apartment_id) is None:
            raise EntityNotFoundError("Apartment", apartment_id)

        resident = Resident(
            first_name=first_name,
            last_name=last_name,
            email=email,
            apartment_id=apartment_id,
            phone=phone,
        )
        if self._residents.exists_by_email(resident.email):
            raise ConflictError(f"Resident with email {resident.email} already exists.")
        return self._residents.add(resident)


class ListResidents:
    def __init__(self, residents: ResidentRepository) -> None:
        self._residents = residents

    def execute(self, apartment_id: int | None = None) -> list[Resident]:
        return self._residents.list(apartment_id)


class GetResident:
    def __init__(self, residents: ResidentRepository) -> None:
        self._residents = residents

    def execute(self, resident_id: int) -> Resident:
        resident = self._residents.get(resident_id)
        if resident is None:
            raise EntityNotFoundError("Resident", resident_id)
        return resident


class UpdateResident:
    def __init__(
        self,
        residents: ResidentRepository,
        apartments: ApartmentRepository,
    ) -> None:
        self._residents = residents
        self._apartments = apartments

    def execute(
        self,
        resident_id: int,
        *,
        first_name: str,
        last_name: str,
        email: str,
        apartment_id: int,
        phone: str | None = None,
    ) -> Resident:
        if self._residents.get(resident_id) is None:
            raise EntityNotFoundError("Resident", resident_id)
        if self._apartments.get(apartment_id) is None:
            raise EntityNotFoundError("Apartment", apartment_id)

        resident = Resident(
            first_name=first_name,
            last_name=last_name,
            email=email,
            apartment_id=apartment_id,
            phone=phone,
            id=resident_id,
        )
        if self._residents.exists_by_email(resident.email, exclude_id=resident_id):
            raise ConflictError(f"Resident with email {resident.email} already exists.")
        return self._residents.update(resident)


class DeleteResident:
    def __init__(self, residents: ResidentRepository) -> None:
        self._residents = residents

    def execute(self, resident_id: int) -> None:
        if self._residents.get(resident_id) is None:
            raise EntityNotFoundError("Resident", resident_id)
        self._residents.delete(resident_id)
