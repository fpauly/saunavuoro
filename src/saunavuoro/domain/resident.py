from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Resident:
    apartment_id: UUID
    name: str
    id: UUID = field(default_factory=uuid4)
