"""Weekly turn use case tests: the in-memory UnitOfWork replaces the database."""

from datetime import time
from uuid import uuid4

import pytest

from saunavuoro.application.errors import AlreadyExistsError, ConflictError, NotFoundError
from saunavuoro.application.use_cases.weekly_turns import (
    AssignWeeklyTurn,
    ChangeWeeklyTurn,
    GetWeeklyTurn,
    ListWeeklyTurns,
    RemoveWeeklyTurn,
)
from saunavuoro.domain.apartment import Apartment
from saunavuoro.domain.errors import RuleViolationError
from saunavuoro.domain.sauna import Sauna
from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork

FRIDAY = 4
SATURDAY = 5


@pytest.fixture
def sauna(uow: InMemoryUnitOfWork) -> Sauna:
    sauna = Sauna(name="Lower sauna", opens_at=time(17), closes_at=time(22))
    uow.saunas.add(sauna)
    return sauna


def add_apartment(uow: InMemoryUnitOfWork, number: str) -> Apartment:
    apartment = Apartment(number=number)
    uow.apartments.add(apartment)
    return apartment


def test_assign_saves_the_turn(uow: InMemoryUnitOfWork, sauna: Sauna) -> None:
    apartment = add_apartment(uow, "A 1")

    turn = AssignWeeklyTurn(uow).execute(sauna.id, apartment.id, FRIDAY, time(18))

    assert uow.weekly_turns.get(turn.id) == turn
    assert uow.committed


def test_assign_to_unknown_sauna_raises_not_found(uow: InMemoryUnitOfWork) -> None:
    apartment = add_apartment(uow, "A 1")
    with pytest.raises(NotFoundError, match="Sauna"):
        AssignWeeklyTurn(uow).execute(uuid4(), apartment.id, FRIDAY, time(18))


def test_assign_to_unknown_apartment_raises_not_found(
    uow: InMemoryUnitOfWork, sauna: Sauna
) -> None:
    with pytest.raises(NotFoundError, match="Apartment"):
        AssignWeeklyTurn(uow).execute(sauna.id, uuid4(), FRIDAY, time(18))


def test_turn_outside_opening_hours_is_rejected(uow: InMemoryUnitOfWork, sauna: Sauna) -> None:
    apartment = add_apartment(uow, "A 1")
    with pytest.raises(RuleViolationError):
        AssignWeeklyTurn(uow).execute(sauna.id, apartment.id, FRIDAY, time(22))
    assert not uow.committed


def test_apartment_can_have_only_one_weekly_turn(uow: InMemoryUnitOfWork, sauna: Sauna) -> None:
    apartment = add_apartment(uow, "A 1")
    AssignWeeklyTurn(uow).execute(sauna.id, apartment.id, FRIDAY, time(18))

    with pytest.raises(AlreadyExistsError, match="A 1 already has a weekly turn"):
        AssignWeeklyTurn(uow).execute(sauna.id, apartment.id, SATURDAY, time(18))


def test_taken_slot_cannot_be_assigned_again(uow: InMemoryUnitOfWork, sauna: Sauna) -> None:
    first = add_apartment(uow, "A 1")
    second = add_apartment(uow, "A 2")
    AssignWeeklyTurn(uow).execute(sauna.id, first.id, FRIDAY, time(18))

    with pytest.raises(ConflictError, match="Fridays at 18:00"):
        AssignWeeklyTurn(uow).execute(sauna.id, second.id, FRIDAY, time(18))


def test_change_moves_the_turn(uow: InMemoryUnitOfWork, sauna: Sauna) -> None:
    apartment = add_apartment(uow, "A 1")
    turn = AssignWeeklyTurn(uow).execute(sauna.id, apartment.id, FRIDAY, time(18))

    ChangeWeeklyTurn(uow).execute(turn.id, sauna.id, apartment.id, SATURDAY, time(20))

    changed = GetWeeklyTurn(uow).execute(turn.id)
    assert (changed.weekday, changed.start_time) == (SATURDAY, time(20))


def test_change_keeps_the_same_slot_without_conflict(uow: InMemoryUnitOfWork, sauna: Sauna) -> None:
    apartment = add_apartment(uow, "A 1")
    turn = AssignWeeklyTurn(uow).execute(sauna.id, apartment.id, FRIDAY, time(18))

    ChangeWeeklyTurn(uow).execute(turn.id, sauna.id, apartment.id, FRIDAY, time(18))


def test_change_to_a_taken_slot_raises_conflict(uow: InMemoryUnitOfWork, sauna: Sauna) -> None:
    first = add_apartment(uow, "A 1")
    second = add_apartment(uow, "A 2")
    AssignWeeklyTurn(uow).execute(sauna.id, first.id, FRIDAY, time(18))
    turn = AssignWeeklyTurn(uow).execute(sauna.id, second.id, FRIDAY, time(19))

    with pytest.raises(ConflictError):
        ChangeWeeklyTurn(uow).execute(turn.id, sauna.id, second.id, FRIDAY, time(18))


def test_change_unknown_turn_raises_not_found(uow: InMemoryUnitOfWork, sauna: Sauna) -> None:
    apartment = add_apartment(uow, "A 1")
    with pytest.raises(NotFoundError, match="Weekly turn"):
        ChangeWeeklyTurn(uow).execute(uuid4(), sauna.id, apartment.id, FRIDAY, time(18))


def test_list_filters_by_sauna_and_apartment(uow: InMemoryUnitOfWork, sauna: Sauna) -> None:
    other_sauna = Sauna(name="Upper sauna", opens_at=time(17), closes_at=time(22))
    uow.saunas.add(other_sauna)
    first = add_apartment(uow, "A 1")
    second = add_apartment(uow, "A 2")
    saturday = AssignWeeklyTurn(uow).execute(sauna.id, first.id, SATURDAY, time(18))
    friday = AssignWeeklyTurn(uow).execute(other_sauna.id, second.id, FRIDAY, time(18))

    assert ListWeeklyTurns(uow).execute() == [friday, saturday]
    assert ListWeeklyTurns(uow).execute(sauna_id=sauna.id) == [saturday]
    assert ListWeeklyTurns(uow).execute(apartment_id=second.id) == [friday]
    assert ListWeeklyTurns(uow).execute(sauna_id=sauna.id, apartment_id=second.id) == []


def test_remove_deletes_the_turn(uow: InMemoryUnitOfWork, sauna: Sauna) -> None:
    apartment = add_apartment(uow, "A 1")
    turn = AssignWeeklyTurn(uow).execute(sauna.id, apartment.id, FRIDAY, time(18))

    RemoveWeeklyTurn(uow).execute(turn.id)

    assert uow.weekly_turns.get(turn.id) is None


def test_remove_unknown_turn_raises_not_found(uow: InMemoryUnitOfWork) -> None:
    with pytest.raises(NotFoundError):
        RemoveWeeklyTurn(uow).execute(uuid4())
