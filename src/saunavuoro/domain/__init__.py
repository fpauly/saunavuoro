"""Public domain API."""

from saunavuoro.domain.entities import Apartment, Resident, Sauna
from saunavuoro.domain.exceptions import DomainError, DomainValidationError

__all__ = [
    "Apartment",
    "DomainError",
    "DomainValidationError",
    "Resident",
    "Sauna",
]
