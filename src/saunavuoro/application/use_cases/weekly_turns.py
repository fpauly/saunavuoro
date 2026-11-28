"""Weekly turn use cases. One class per use case, each with an execute() method."""

from datetime import time
from uuid import UUID

from saunavuoro.application.errors import AlreadyExistsError, ConflictError, NotFoundError
from saunavuoro.application.ports import UnitOfWork
from saunavuoro.domain.weekly_turn import WEEKDAY_NAMES, WeeklyTurn


def _check_turn_is_allowed(uow: UnitOfWork, turn: WeeklyTurn) -> None:
    """Shared checks for assigning and changing a turn. Must be called inside the unit of work."""
    sauna = uow.saunas.get(turn.sauna_id)
    if sauna is None:
        raise NotFoundError("Sauna", turn.sauna_id)
    apartment = uow.apartments.get(turn.apartment_id)
    if apartment is None:
        raise NotFoundError("Apartment", turn.apartment_id)

    turn.check_fits(sauna)

    own_turn = uow.weekly_turns.get_by_apartment(turn.apartment_id)
    if own_turn is not None and own_turn.id != turn.id:
        raise AlreadyExistsError(f"Apartment {apartment.number} already has a weekly turn.")

    slot_owner = uow.weekly_turns.get_by_slot(turn.sauna_id, turn.weekday, turn.start_time)
    if slot_owner is not None and slot_owner.id != turn.id:
        raise ConflictError(
            f"{sauna.name} is already taken on {WEEKDAY_NAMES[turn.weekday]}s "
            f"at {turn.start_time.strftime('%H:%M')}."
        )


class AssignWeeklyTurn:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(
        self, sauna_id: UUID, apartment_id: UUID, weekday: int, start_time: time
    ) -> WeeklyTurn:
        turn = WeeklyTurn(
            sauna_id=sauna_id, apartment_id=apartment_id, weekday=weekday, start_time=start_time
        )
        with self._uow as uow:
            _check_turn_is_allowed(uow, turn)
            uow.weekly_turns.add(turn)
            uow.commit()
        return turn


class GetWeeklyTurn:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, turn_id: UUID) -> WeeklyTurn:
        with self._uow as uow:
            turn = uow.weekly_turns.get(turn_id)
        if turn is None:
            raise NotFoundError("Weekly turn", turn_id)
        return turn


class ListWeeklyTurns:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(
        self, sauna_id: UUID | None = None, apartment_id: UUID | None = None
    ) -> list[WeeklyTurn]:
        with self._uow as uow:
            if sauna_id is not None:
                turns = uow.weekly_turns.list_by_sauna(sauna_id)
            else:
                turns = uow.weekly_turns.list_all()
        if apartment_id is not None:
            turns = [t for t in turns if t.apartment_id == apartment_id]
        return turns


class ChangeWeeklyTurn:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(
        self, turn_id: UUID, sauna_id: UUID, apartment_id: UUID, weekday: int, start_time: time
    ) -> WeeklyTurn:
        turn = WeeklyTurn(
            id=turn_id,
            sauna_id=sauna_id,
            apartment_id=apartment_id,
            weekday=weekday,
            start_time=start_time,
        )
        with self._uow as uow:
            if uow.weekly_turns.get(turn_id) is None:
                raise NotFoundError("Weekly turn", turn_id)
            _check_turn_is_allowed(uow, turn)
            uow.weekly_turns.update(turn)
            uow.commit()
        return turn


class RemoveWeeklyTurn:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(self, turn_id: UUID) -> None:
        with self._uow as uow:
            if uow.weekly_turns.get(turn_id) is None:
                raise NotFoundError("Weekly turn", turn_id)
            uow.weekly_turns.delete(turn_id)
            uow.commit()
