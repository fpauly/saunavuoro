"""SQLAlchemy implementation of ApartmentRepository.

Converts between the ORM model (database) and the domain entity.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from saunavuoro.domain.apartment import Apartment
from saunavuoro.infrastructure.persistence.models import ApartmentModel


def _to_entity(row: ApartmentModel) -> Apartment:
    return Apartment(id=row.id, number=row.number)


class SqlAlchemyApartmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, apartment: Apartment) -> None:
        self._session.add(ApartmentModel(id=apartment.id, number=apartment.number))

    def get(self, apartment_id: UUID) -> Apartment | None:
        row = self._session.get(ApartmentModel, apartment_id)
        return _to_entity(row) if row else None

    def get_by_number(self, number: str) -> Apartment | None:
        row = self._session.scalar(select(ApartmentModel).where(ApartmentModel.number == number))
        return _to_entity(row) if row else None

    def list_all(self) -> list[Apartment]:
        rows = self._session.scalars(select(ApartmentModel).order_by(ApartmentModel.number))
        return [_to_entity(row) for row in rows]

    def update(self, apartment: Apartment) -> None:
        row = self._session.get(ApartmentModel, apartment.id)
        if row is not None:
            row.number = apartment.number

    def delete(self, apartment_id: UUID) -> None:
        row = self._session.get(ApartmentModel, apartment_id)
        if row is not None:
            self._session.delete(row)
