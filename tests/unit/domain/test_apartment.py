"""Domain tests: plain Python, no database, no web framework."""

import pytest

from saunavuoro.domain.apartment import Apartment
from saunavuoro.domain.errors import InvalidApartmentNumberError


def test_number_is_trimmed_and_upper_case() -> None:
    assert Apartment(number="  a 12 ").number == "A 12"


def test_empty_number_is_rejected() -> None:
    with pytest.raises(InvalidApartmentNumberError):
        Apartment(number="   ")


def test_too_long_number_is_rejected() -> None:
    with pytest.raises(InvalidApartmentNumberError):
        Apartment(number="A" * 21)
