"""Sauna use case tests: the in-memory UnitOfWork replaces the database."""

from datetime import time
from uuid import uuid4

import pytest

from saunavuoro.application.errors import NotFoundError
from saunavuoro.application.use_cases.saunas import (
    CreateSauna,
    DeleteSauna,
    GetSauna,
    UpdateSauna,
)
from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork


def test_create_sauna_saves_opening_hours_and_rules(uow: InMemoryUnitOfWork) -> None:
    sauna = CreateSauna(uow).execute(
        "Lower sauna",
        time(17),
        time(22),
        turn_length_minutes=90,
        max_extra_bookings_per_week=3,
        max_days_ahead=30,
        cancellation_deadline_hours=4,
    )

    assert uow.saunas.get(sauna.id) == sauna
    assert sauna.turn_start_times() == [time(17), time(18, 30), time(20)]
    assert sauna.max_extra_bookings_per_week == 3
    assert sauna.max_days_ahead == 30
    assert sauna.cancellation_deadline_hours == 4
    assert uow.committed


def test_update_sauna_changes_opening_hours_and_rules(uow: InMemoryUnitOfWork) -> None:
    sauna = CreateSauna(uow).execute("Lower sauna", time(17), time(22))

    UpdateSauna(uow).execute(
        sauna.id,
        "Upper sauna",
        time(18),
        time(21),
        turn_length_minutes=30,
        max_extra_bookings_per_week=0,
        max_days_ahead=7,
        cancellation_deadline_hours=1,
    )

    updated = GetSauna(uow).execute(sauna.id)
    assert updated.name == "Upper sauna"
    assert updated.opens_at == time(18)
    assert updated.closes_at == time(21)
    assert updated.turn_length_minutes == 30
    assert updated.max_extra_bookings_per_week == 0
    assert updated.max_days_ahead == 7
    assert updated.cancellation_deadline_hours == 1


def test_get_unknown_sauna_raises_not_found(uow: InMemoryUnitOfWork) -> None:
    with pytest.raises(NotFoundError):
        GetSauna(uow).execute(uuid4())


def test_delete_unknown_sauna_raises_not_found(uow: InMemoryUnitOfWork) -> None:
    with pytest.raises(NotFoundError):
        DeleteSauna(uow).execute(uuid4())
