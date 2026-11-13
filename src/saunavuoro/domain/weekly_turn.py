from dataclasses import dataclass, field
from datetime import time
from uuid import UUID, uuid4


@dataclass
class WeeklyTurn:
    sauna_id: UUID
    apartment_id: UUID
    weekday: int
    start_time: time
    id: UUID = field(default_factory=uuid4)
