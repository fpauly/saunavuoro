from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Booking:
    sauna_id: UUID
    apartment_id: UUID
    starts_at: datetime
    ends_at: datetime
    id: UUID = field(default_factory=uuid4)
