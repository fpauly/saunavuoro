from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session, sessionmaker

from saunavuoro.infrastructure.persistence.apartment_repository import (
    SqlAlchemyApartmentRepository,
)


class SqlAlchemyUnitOfWork:
    """Opens a session on enter; rolls back anything not committed on exit."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self.apartments = SqlAlchemyApartmentRepository(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._session.rollback()  # no effect if commit() was already called
        self._session.close()

    def commit(self) -> None:
        self._session.commit()
