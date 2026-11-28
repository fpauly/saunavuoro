from dataclasses import dataclass, field
from datetime import time
from uuid import UUID, uuid4

from saunavuoro.domain.errors import RuleViolationError
from saunavuoro.domain.sauna import Sauna

WEEKDAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


@dataclass
class WeeklyTurn:
    """A fixed turn that an apartment has in the same sauna every week.

    `weekday` follows Python's `date.weekday()`: 0 is Monday and 6 is Sunday.
    """

    sauna_id: UUID
    apartment_id: UUID
    weekday: int
    start_time: time
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not 0 <= self.weekday <= 6:
            raise RuleViolationError("Weekday must be between 0 (Monday) and 6 (Sunday).")

    def check_fits(self, sauna: Sauna) -> None:
        """Raise RuleViolationError if the turn does not start on one of the sauna's turns."""
        if not sauna.is_turn_start(self.start_time):
            allowed = ", ".join(t.strftime("%H:%M") for t in sauna.turn_start_times())
            raise RuleViolationError(f"A turn in {sauna.name} must start at one of: {allowed}.")
