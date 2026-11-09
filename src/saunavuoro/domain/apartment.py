"""Apartment entity. Domain code is plain Python: no FastAPI, no SQLAlchemy."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from saunavuoro.domain.errors import InvalidApartmentNumberError

MAX_NUMBER_LENGTH = 20


@dataclass
class Apartment:
    number: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.number = self._validate_number(self.number)

    @staticmethod
    def _validate_number(number: str) -> str:
        cleaned = number.strip().upper()
        if not cleaned:
            raise InvalidApartmentNumberError("Apartment number must not be empty.")
        if len(cleaned) > MAX_NUMBER_LENGTH:
            raise InvalidApartmentNumberError(
                f"Apartment number must be at most {MAX_NUMBER_LENGTH} characters."
            )
        return cleaned
