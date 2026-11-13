from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from uuid import UUID, uuid4

from saunavuoro.domain.errors import RuleViolationError


@dataclass
class Sauna:
    name: str
    opens_at: time
    closes_at: time
    turn_length_minutes: int = 60
    max_extra_bookings_per_week: int = 1
    max_days_ahead: int = 14
    cancellation_deadline_hours: int = 2
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise RuleViolationError("Sauna name must not be empty.")
        if self.closes_at <= self.opens_at:
            raise RuleViolationError("Sauna must close after it opens.")
        if self.turn_length_minutes <= 0:
            raise RuleViolationError("Turn length must be positive.")
        if not self.turn_start_times():
            raise RuleViolationError("Opening hours are shorter than one turn.")
        if min(
            self.max_extra_bookings_per_week,
            self.max_days_ahead,
            self.cancellation_deadline_hours,
        ) < 0:
            raise RuleViolationError("Booking rules must not be negative.")

    def turn_start_times(self) -> list[time]:
        day = date(2000, 1, 1)
        start = datetime.combine(day, self.opens_at)
        close = datetime.combine(day, self.closes_at)
        length = timedelta(minutes=self.turn_length_minutes)
        starts: list[time] = []
        while start + length <= close:
            starts.append(start.time())
            start += length
        return starts

    def is_turn_start(self, value: time) -> bool:
        return value in self.turn_start_times()

    def turn_end(self, starts_at: datetime) -> datetime:
        return starts_at + timedelta(minutes=self.turn_length_minutes)
