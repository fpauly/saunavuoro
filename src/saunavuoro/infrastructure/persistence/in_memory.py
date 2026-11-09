"""In-memory implementations of the ports. Used in tests instead of a database."""

from types import TracebackType
from typing import Self
from uuid import UUID

from saunavuoro.domain.apartment import Apartment


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


class InMemoryUnitOfWork:
    def __init__(self) -> None:
        self.apartments = InMemoryApartmentRepository()
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
