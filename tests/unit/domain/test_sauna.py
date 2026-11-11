from datetime import UTC, datetime, time

import pytest

from saunavuoro.domain.errors import RuleViolationError
from saunavuoro.domain.sauna import Sauna


def test_turns_fit_inside_opening_hours() -> None:
    sauna = Sauna(name="A", opens_at=time(17), closes_at=time(20, 30))
    assert sauna.turn_start_times() == [time(17), time(18), time(19)]
    assert sauna.is_turn_start(time(19))
    assert not sauna.is_turn_start(time(20))
    assert not sauna.is_turn_start(time(17, 30))


def test_turn_end() -> None:
    sauna = Sauna(name="A", opens_at=time(17), closes_at=time(22), turn_length_minutes=90)
    start = datetime(2026, 11, 20, 17, tzinfo=UTC)
    assert sauna.turn_end(start) == datetime(2026, 11, 20, 18, 30, tzinfo=UTC)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": " "},
        {"closes_at": time(17)},
        {"turn_length_minutes": 0},
        {"turn_length_minutes": 300},
        {"max_days_ahead": -1},
    ],
)
def test_invalid_sauna(kwargs: dict[str, object]) -> None:
    data: dict[str, object] = {"name": "A", "opens_at": time(17), "closes_at": time(21)} | kwargs
    with pytest.raises(RuleViolationError):
        Sauna(**data)  # type: ignore[arg-type]
