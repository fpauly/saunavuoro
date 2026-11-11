"""In-memory implementations of the ports. Used in tests instead of a database."""

from datetime import datetime, time
from types import TracebackType
from typing import Self
from uuid import UUID

from saunavuoro.domain.apartment import Apartment
from saunavuoro.domain.booking import Booking
from saunavuoro.domain.resident import Resident
from saunavuoro.domain.sauna import Sauna
from saunavuoro.domain.weekly_turn import WeeklyTurn


class InMemoryApartmentRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, Apartment] = {}

    def add(self, apartment: Apartment) -> None:
        self.items[apartment.id] = apartment

    def get(self, apartment_id: UUID) -> Apartment | None:
        return self.items.get(apartment_id)

    def get_by_number(self, number: str) -> Apartment | None:
        return next((a for a in self.items.values() if a.number == number), None)

    def list_all(self) -> list[Apartment]:
        return sorted(self.items.values(), key=lambda a: a.number)

    def update(self, apartment: Apartment) -> None:
        self.items[apartment.id] = apartment

    def delete(self, apartment_id: UUID) -> None:
        self.items.pop(apartment_id, None)


class InMemoryResidentRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, Resident] = {}

    def add(self, resident: Resident) -> None:
        self.items[resident.id] = resident

    def get(self, resident_id: UUID) -> Resident | None:
        return self.items.get(resident_id)

    def list_by_apartment(self, apartment_id: UUID) -> list[Resident]:
        found = [r for r in self.items.values() if r.apartment_id == apartment_id]
        return sorted(found, key=lambda r: r.name)

    def update(self, resident: Resident) -> None:
        self.items[resident.id] = resident

    def delete(self, resident_id: UUID) -> None:
        self.items.pop(resident_id, None)


class InMemorySaunaRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, Sauna] = {}

    def add(self, sauna: Sauna) -> None:
        self.items[sauna.id] = sauna

    def get(self, sauna_id: UUID) -> Sauna | None:
        return self.items.get(sauna_id)

    def list_all(self) -> list[Sauna]:
        return sorted(self.items.values(), key=lambda s: s.name)

    def update(self, sauna: Sauna) -> None:
        self.items[sauna.id] = sauna

    def delete(self, sauna_id: UUID) -> None:
        self.items.pop(sauna_id, None)


class InMemoryWeeklyTurnRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, WeeklyTurn] = {}

    def add(self, turn: WeeklyTurn) -> None:
        self.items[turn.id] = turn

    def get(self, turn_id: UUID) -> WeeklyTurn | None:
        return self.items.get(turn_id)

    def get_by_apartment(self, apartment_id: UUID) -> WeeklyTurn | None:
        return next((t for t in self.items.values() if t.apartment_id == apartment_id), None)

    def get_by_slot(self, sauna_id: UUID, weekday: int, start_time: time) -> WeeklyTurn | None:
        return next(
            (
                t
                for t in self.items.values()
                if (t.sauna_id, t.weekday, t.start_time) == (sauna_id, weekday, start_time)
            ),
            None,
        )

    def list_by_sauna(self, sauna_id: UUID) -> list[WeeklyTurn]:
        found = [t for t in self.items.values() if t.sauna_id == sauna_id]
        return sorted(found, key=lambda t: (t.weekday, t.start_time))

    def update(self, turn: WeeklyTurn) -> None:
        self.items[turn.id] = turn

    def delete(self, turn_id: UUID) -> None:
        self.items.pop(turn_id, None)


class InMemoryBookingRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, Booking] = {}

    def add(self, booking: Booking) -> None:
        self.items[booking.id] = booking

    def get(self, booking_id: UUID) -> Booking | None:
        return self.items.get(booking_id)

    def get_by_slot(self, sauna_id: UUID, starts_at: datetime) -> Booking | None:
        return next(
            (
                b
                for b in self.items.values()
                if b.sauna_id == sauna_id and b.starts_at == starts_at
            ),
            None,
        )

    def list_by_sauna(self, sauna_id: UUID, start: datetime, end: datetime) -> list[Booking]:
        found = [
            b for b in self.items.values() if b.sauna_id == sauna_id and start <= b.starts_at < end
        ]
        return sorted(found, key=lambda b: b.starts_at)

    def list_by_apartment(
        self, apartment_id: UUID, start: datetime, end: datetime
    ) -> list[Booking]:
        found = [
            b
            for b in self.items.values()
            if b.apartment_id == apartment_id and start <= b.starts_at < end
        ]
        return sorted(found, key=lambda b: b.starts_at)

    def delete(self, booking_id: UUID) -> None:
        self.items.pop(booking_id, None)


class InMemoryUnitOfWork:
    def __init__(self) -> None:
        self.apartments = InMemoryApartmentRepository()
        self.residents = InMemoryResidentRepository()
        self.saunas = InMemorySaunaRepository()
        self.weekly_turns = InMemoryWeeklyTurnRepository()
        self.bookings = InMemoryBookingRepository()
        self.committed = False

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        pass

    def commit(self) -> None:
        self.committed = True
