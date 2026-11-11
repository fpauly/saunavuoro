from types import TracebackType
from typing import Self

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from saunavuoro.application.errors import ConflictError
from saunavuoro.infrastructure.persistence.apartment_repository import (
    SqlAlchemyApartmentRepository,
)
from saunavuoro.infrastructure.persistence.booking_repository import SqlAlchemyBookingRepository
from saunavuoro.infrastructure.persistence.resident_repository import (
    SqlAlchemyResidentRepository,
)
from saunavuoro.infrastructure.persistence.sauna_repository import SqlAlchemySaunaRepository
from saunavuoro.infrastructure.persistence.weekly_turn_repository import (
    SqlAlchemyWeeklyTurnRepository,
)


class SqlAlchemyUnitOfWork:
    """Opens a session on enter; rolls back anything not committed on exit."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def __enter__(self) -> Self:
        self._session = self._session_factory()
        self.apartments = SqlAlchemyApartmentRepository(self._session)
        self.residents = SqlAlchemyResidentRepository(self._session)
        self.saunas = SqlAlchemySaunaRepository(self._session)
        self.weekly_turns = SqlAlchemyWeeklyTurnRepository(self._session)
        self.bookings = SqlAlchemyBookingRepository(self._session)
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
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise ConflictError("The change conflicts with existing data.") from exc
