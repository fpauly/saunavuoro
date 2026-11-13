"""Domain entities and their business rules.

Entities are immutable value-like objects. They validate themselves on
creation, so an entity instance can never be in an invalid state.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from saunavuoro.domain.exceptions import DomainValidationError

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _required_text(value: str, field: str, max_length: int) -> str:
    normalized = value.strip()
    if not normalized:
        raise DomainValidationError(f"{field} is required.")
    if len(normalized) > max_length:
        raise DomainValidationError(f"{field} must be at most {max_length} characters.")
    return normalized


def _optional_text(value: str | None, field: str, max_length: int) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > max_length:
        raise DomainValidationError(f"{field} must be at most {max_length} characters.")
    return normalized


@dataclass(frozen=True, slots=True)
class Apartment:
    """An apartment in the building. Apartment numbers are unique."""

    number: str
    floor: int
    id: int | None = None

    def __post_init__(self) -> None:
        number = _required_text(self.number, "Apartment number", 20).upper()
        object.__setattr__(self, "number", number)
        if self.floor < 1:
            raise DomainValidationError("Floor must be at least 1.")


@dataclass(frozen=True, slots=True)
class Resident:
    """A person living in an apartment. Email addresses are unique."""

    first_name: str
    last_name: str
    email: str
    apartment_id: int
    phone: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "first_name", _required_text(self.first_name, "First name", 100))
        object.__setattr__(self, "last_name", _required_text(self.last_name, "Last name", 100))
        email = _required_text(self.email, "Email", 254).lower()
        if not _EMAIL_PATTERN.match(email):
            raise DomainValidationError("Email must be a valid email address.")
        object.__setattr__(self, "email", email)
        object.__setattr__(self, "phone", _optional_text(self.phone, "Phone", 30))
        if self.apartment_id < 1:
            raise DomainValidationError("Apartment id must be positive.")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass(frozen=True, slots=True)
class Sauna:
    """A shared sauna in the building. Sauna names are unique."""

    name: str
    location: str
    capacity: int
    description: str | None = None
    id: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _required_text(self.name, "Sauna name", 100))
        object.__setattr__(self, "location", _required_text(self.location, "Location", 200))
        object.__setattr__(
            self, "description", _optional_text(self.description, "Description", 500)
        )
        if self.capacity < 1:
            raise DomainValidationError("Capacity must be at least 1.")
        if self.capacity > 1000:
            raise DomainValidationError("Capacity must be at most 1000.")
