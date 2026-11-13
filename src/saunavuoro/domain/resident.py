from dataclasses import dataclass, field
from uuid import UUID, uuid4

from saunavuoro.domain.errors import RuleViolationError

MAX_NAME_LENGTH = 100


@dataclass
class Resident:
    apartment_id: UUID
    name: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise RuleViolationError("Resident name must not be empty.")
        if len(self.name) > MAX_NAME_LENGTH:
            raise RuleViolationError(
                f"Resident name must be at most {MAX_NAME_LENGTH} characters."
            )
