from datetime import time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from saunavuoro.domain.weekly_turn import WeeklyTurn
from saunavuoro.infrastructure.persistence.models import WeeklyTurnModel


def _to_entity(row: WeeklyTurnModel) -> WeeklyTurn:
    return WeeklyTurn(
        id=row.id,
        sauna_id=row.sauna_id,
        apartment_id=row.apartment_id,
        weekday=row.weekday,
        start_time=row.start_time,
    )


class SqlAlchemyWeeklyTurnRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, turn: WeeklyTurn) -> None:
        self._session.add(
            WeeklyTurnModel(
                id=turn.id,
                sauna_id=turn.sauna_id,
                apartment_id=turn.apartment_id,
                weekday=turn.weekday,
                start_time=turn.start_time,
            )
        )

    def get(self, turn_id: UUID) -> WeeklyTurn | None:
        row = self._session.get(WeeklyTurnModel, turn_id)
        return _to_entity(row) if row else None

    def get_by_apartment(self, apartment_id: UUID) -> WeeklyTurn | None:
        row = self._session.scalar(
            select(WeeklyTurnModel).where(WeeklyTurnModel.apartment_id == apartment_id)
        )
        return _to_entity(row) if row else None

    def get_by_slot(self, sauna_id: UUID, weekday: int, start_time: time) -> WeeklyTurn | None:
        row = self._session.scalar(
            select(WeeklyTurnModel).where(
                WeeklyTurnModel.sauna_id == sauna_id,
                WeeklyTurnModel.weekday == weekday,
                WeeklyTurnModel.start_time == start_time,
            )
        )
        return _to_entity(row) if row else None

    def list_by_sauna(self, sauna_id: UUID) -> list[WeeklyTurn]:
        rows = self._session.scalars(
            select(WeeklyTurnModel)
            .where(WeeklyTurnModel.sauna_id == sauna_id)
            .order_by(WeeklyTurnModel.weekday, WeeklyTurnModel.start_time)
        )
        return [_to_entity(row) for row in rows]

    def update(self, turn: WeeklyTurn) -> None:
        row = self._session.get(WeeklyTurnModel, turn.id)
        if row is not None:
            row.sauna_id = turn.sauna_id
            row.apartment_id = turn.apartment_id
            row.weekday = turn.weekday
            row.start_time = turn.start_time

    def delete(self, turn_id: UUID) -> None:
        row = self._session.get(WeeklyTurnModel, turn_id)
        if row is not None:
            self._session.delete(row)
