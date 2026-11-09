"""Ports: interfaces the use cases depend on.

The infrastructure layer implements them (SQLAlchemy, in-memory).
To add a new resource, add its repository Protocol here and a property in UnitOfWork.
"""

from types import TracebackType
from typing import Protocol, Self
from uuid import UUID

from saunavuoro.domain.apartment import Apartment


class ApartmentRepository(Protocol):
    def add(self, apartment: Apartment) -> None: ...
    def get(self, apartment_id: UUID) -> Apartment | None: ...
    def get_by_number(self, number: str) -> Apartment | None: ...
    def list_all(self) -> list[Apartment]: ...
    def update(self, apartment: Apartment) -> None: ...
    def delete(self, apartment_id: UUID) -> None: ...


class UnitOfWork(Protocol):
    """One database transaction. Changes are saved only when commit() is called."""

    @property
    def apartments(self) -> ApartmentRepository: ...

    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
    def commit(self) -> None: ...
