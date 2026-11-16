from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from saunavuoro.domain.resident import Resident
from saunavuoro.infrastructure.persistence.models import ResidentModel


def _to_entity(row: ResidentModel) -> Resident:
    return Resident(id=row.id, apartment_id=row.apartment_id, name=row.name)


class SqlAlchemyResidentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, resident: Resident) -> None:
        self._session.add(
            ResidentModel(id=resident.id, apartment_id=resident.apartment_id, name=resident.name)
        )

    def get(self, resident_id: UUID) -> Resident | None:
        row = self._session.get(ResidentModel, resident_id)
        return _to_entity(row) if row else None

    def list_all(self) -> list[Resident]:
        rows = self._session.scalars(select(ResidentModel).order_by(ResidentModel.name))
        return [_to_entity(row) for row in rows]

    def list_by_apartment(self, apartment_id: UUID) -> list[Resident]:
        rows = self._session.scalars(
            select(ResidentModel)
            .where(ResidentModel.apartment_id == apartment_id)
            .order_by(ResidentModel.name)
        )
        return [_to_entity(row) for row in rows]

    def update(self, resident: Resident) -> None:
        row = self._session.get(ResidentModel, resident.id)
        if row is not None:
            row.apartment_id = resident.apartment_id
            row.name = resident.name

    def delete(self, resident_id: UUID) -> None:
        row = self._session.get(ResidentModel, resident_id)
        if row is not None:
            self._session.delete(row)
