"""SQLAlchemy repository implementations for the application ports."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from saunavuoro.application.exceptions import EntityNotFoundError
from saunavuoro.domain.entities import Apartment, Resident, Sauna
from saunavuoro.infrastructure.models import ApartmentModel, ResidentModel, SaunaModel


def _apartment_to_domain(model: ApartmentModel) -> Apartment:
    return Apartment(id=model.id, number=model.number, floor=model.floor)


def _resident_to_domain(model: ResidentModel) -> Resident:
    return Resident(
        id=model.id,
        first_name=model.first_name,
        last_name=model.last_name,
        email=model.email,
        apartment_id=model.apartment_id,
        phone=model.phone,
    )


def _sauna_to_domain(model: SaunaModel) -> Sauna:
    return Sauna(
        id=model.id,
        name=model.name,
        location=model.location,
        capacity=model.capacity,
        description=model.description,
    )


class SqlAlchemyApartmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, apartment: Apartment) -> Apartment:
        model = ApartmentModel(number=apartment.number, floor=apartment.floor)
        self._session.add(model)
        self._session.flush()
        return _apartment_to_domain(model)

    def get(self, apartment_id: int) -> Apartment | None:
        model = self._session.get(ApartmentModel, apartment_id)
        return None if model is None else _apartment_to_domain(model)

    def list(self) -> list[Apartment]:
        models = self._session.scalars(select(ApartmentModel).order_by(ApartmentModel.id))
        return [_apartment_to_domain(model) for model in models]

    def update(self, apartment: Apartment) -> Apartment:
        if apartment.id is None:
            raise ValueError("Cannot update an apartment without an id.")
        model = self._session.get(ApartmentModel, apartment.id)
        if model is None:
            raise EntityNotFoundError("Apartment", apartment.id)
        model.number = apartment.number
        model.floor = apartment.floor
        self._session.flush()
        return _apartment_to_domain(model)

    def delete(self, apartment_id: int) -> None:
        model = self._session.get(ApartmentModel, apartment_id)
        if model is not None:
            self._session.delete(model)
            self._session.flush()

    def exists_by_number(self, number: str, exclude_id: int | None = None) -> bool:
        statement = select(ApartmentModel.id).where(
            func.lower(ApartmentModel.number) == number.lower()
        )
        if exclude_id is not None:
            statement = statement.where(ApartmentModel.id != exclude_id)
        return self._session.scalar(statement) is not None


class SqlAlchemyResidentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, resident: Resident) -> Resident:
        model = ResidentModel(
            first_name=resident.first_name,
            last_name=resident.last_name,
            email=resident.email,
            phone=resident.phone,
            apartment_id=resident.apartment_id,
        )
        self._session.add(model)
        self._session.flush()
        return _resident_to_domain(model)

    def get(self, resident_id: int) -> Resident | None:
        model = self._session.get(ResidentModel, resident_id)
        return None if model is None else _resident_to_domain(model)

    def list(self, apartment_id: int | None = None) -> list[Resident]:
        statement = select(ResidentModel).order_by(ResidentModel.id)
        if apartment_id is not None:
            statement = statement.where(ResidentModel.apartment_id == apartment_id)
        models = self._session.scalars(statement)
        return [_resident_to_domain(model) for model in models]

    def update(self, resident: Resident) -> Resident:
        if resident.id is None:
            raise ValueError("Cannot update a resident without an id.")
        model = self._session.get(ResidentModel, resident.id)
        if model is None:
            raise EntityNotFoundError("Resident", resident.id)
        model.first_name = resident.first_name
        model.last_name = resident.last_name
        model.email = resident.email
        model.phone = resident.phone
        model.apartment_id = resident.apartment_id
        self._session.flush()
        return _resident_to_domain(model)

    def delete(self, resident_id: int) -> None:
        model = self._session.get(ResidentModel, resident_id)
        if model is not None:
            self._session.delete(model)
            self._session.flush()

    def exists_by_email(self, email: str, exclude_id: int | None = None) -> bool:
        statement = select(ResidentModel.id).where(func.lower(ResidentModel.email) == email.lower())
        if exclude_id is not None:
            statement = statement.where(ResidentModel.id != exclude_id)
        return self._session.scalar(statement) is not None

    def count_by_apartment(self, apartment_id: int) -> int:
        statement = (
            select(func.count())
            .select_from(ResidentModel)
            .where(ResidentModel.apartment_id == apartment_id)
        )
        return int(self._session.scalar(statement) or 0)


class SqlAlchemySaunaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, sauna: Sauna) -> Sauna:
        model = SaunaModel(
            name=sauna.name,
            location=sauna.location,
            capacity=sauna.capacity,
            description=sauna.description,
        )
        self._session.add(model)
        self._session.flush()
        return _sauna_to_domain(model)

    def get(self, sauna_id: int) -> Sauna | None:
        model = self._session.get(SaunaModel, sauna_id)
        return None if model is None else _sauna_to_domain(model)

    def list(self) -> list[Sauna]:
        models = self._session.scalars(select(SaunaModel).order_by(SaunaModel.id))
        return [_sauna_to_domain(model) for model in models]

    def update(self, sauna: Sauna) -> Sauna:
        if sauna.id is None:
            raise ValueError("Cannot update a sauna without an id.")
        model = self._session.get(SaunaModel, sauna.id)
        if model is None:
            raise EntityNotFoundError("Sauna", sauna.id)
        model.name = sauna.name
        model.location = sauna.location
        model.capacity = sauna.capacity
        model.description = sauna.description
        self._session.flush()
        return _sauna_to_domain(model)

    def delete(self, sauna_id: int) -> None:
        model = self._session.get(SaunaModel, sauna_id)
        if model is not None:
            self._session.delete(model)
            self._session.flush()

    def exists_by_name(self, name: str, exclude_id: int | None = None) -> bool:
        statement = select(SaunaModel.id).where(func.lower(SaunaModel.name) == name.lower())
        if exclude_id is not None:
            statement = statement.where(SaunaModel.id != exclude_id)
        return self._session.scalar(statement) is not None
