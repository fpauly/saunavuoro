from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from saunavuoro.domain.sauna import Sauna
from saunavuoro.infrastructure.persistence.models import SaunaModel

_FIELDS = (
    "name",
    "opens_at",
    "closes_at",
    "turn_length_minutes",
    "max_extra_bookings_per_week",
    "max_days_ahead",
    "cancellation_deadline_hours",
)


def _to_entity(row: SaunaModel) -> Sauna:
    return Sauna(id=row.id, **{name: getattr(row, name) for name in _FIELDS})


class SqlAlchemySaunaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, sauna: Sauna) -> None:
        values = {name: getattr(sauna, name) for name in _FIELDS}
        self._session.add(SaunaModel(id=sauna.id, **values))

    def get(self, sauna_id: UUID) -> Sauna | None:
        row = self._session.get(SaunaModel, sauna_id)
        return _to_entity(row) if row else None

    def list_all(self) -> list[Sauna]:
        rows = self._session.scalars(select(SaunaModel).order_by(SaunaModel.name))
        return [_to_entity(row) for row in rows]

    def update(self, sauna: Sauna) -> None:
        row = self._session.get(SaunaModel, sauna.id)
        if row is not None:
            for name in _FIELDS:
                setattr(row, name, getattr(sauna, name))

    def delete(self, sauna_id: UUID) -> None:
        row = self._session.get(SaunaModel, sauna_id)
        if row is not None:
            self._session.delete(row)
