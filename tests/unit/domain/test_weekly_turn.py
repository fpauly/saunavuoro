from datetime import time
from uuid import uuid4

import pytest

from saunavuoro.domain.errors import RuleViolationError
from saunavuoro.domain.sauna import Sauna
from saunavuoro.domain.weekly_turn import WeeklyTurn

SAUNA = Sauna(name="Lower sauna", opens_at=time(17), closes_at=time(21))


def make_turn(weekday: int = 4, start_time: time = time(18)) -> WeeklyTurn:
    return WeeklyTurn(
        sauna_id=SAUNA.id, apartment_id=uuid4(), weekday=weekday, start_time=start_time
    )


@pytest.mark.parametrize("weekday", [0, 6])
def test_weekday_from_monday_to_sunday_is_allowed(weekday: int) -> None:
    assert make_turn(weekday=weekday).weekday == weekday


@pytest.mark.parametrize("weekday", [-1, 7])
def test_weekday_outside_the_week_is_rejected(weekday: int) -> None:
    with pytest.raises(RuleViolationError):
        make_turn(weekday=weekday)


def test_turn_on_a_turn_start_fits_the_sauna() -> None:
    make_turn(start_time=time(20)).check_fits(SAUNA)


@pytest.mark.parametrize("start_time", [time(16), time(18, 30), time(21)])
def test_turn_outside_the_turn_grid_does_not_fit(start_time: time) -> None:
    with pytest.raises(RuleViolationError, match="17:00, 18:00, 19:00, 20:00"):
        make_turn(start_time=start_time).check_fits(SAUNA)
