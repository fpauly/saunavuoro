from datetime import UTC, datetime, time, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from saunavuoro.application.errors import ConflictError
from saunavuoro.domain.apartment import Apartment
from saunavuoro.domain.booking import Booking
from saunavuoro.domain.resident import Resident
from saunavuoro.domain.sauna import Sauna
from saunavuoro.domain.weekly_turn import WeeklyTurn
from saunavuoro.infrastructure.clock import HELSINKI
from saunavuoro.infrastructure.persistence import models  # noqa: F401
from saunavuoro.infrastructure.persistence.database import Base
from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork
from saunavuoro.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork


def make_sql_uow() -> SqlAlchemyUnitOfWork:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    return SqlAlchemyUnitOfWork(sessionmaker(bind=engine, expire_on_commit=False))


@pytest.fixture(params=["sql", "memory"])
def any_uow(request: pytest.FixtureRequest) -> SqlAlchemyUnitOfWork | InMemoryUnitOfWork:
    return make_sql_uow() if request.param == "sql" else InMemoryUnitOfWork()


def test_all_repositories_save_and_load(
    any_uow: SqlAlchemyUnitOfWork | InMemoryUnitOfWork,
) -> None:
    apartment = Apartment(number="A 1")
    resident = Resident(apartment_id=apartment.id, name="Matti")
    sauna = Sauna(name="Lower", opens_at=time(17), closes_at=time(22))
    turn = WeeklyTurn(sauna_id=sauna.id, apartment_id=apartment.id, weekday=4, start_time=time(18))
    starts = datetime(2026, 11, 20, 19, tzinfo=HELSINKI)
    booking = Booking(sauna.id, apartment.id, starts, sauna.turn_end(starts))
    with any_uow as uow:
        uow.apartments.add(apartment)
        uow.saunas.add(sauna)
        uow.commit()
        uow.residents.add(resident)
        uow.weekly_turns.add(turn)
        uow.bookings.add(booking)
        uow.commit()

    with any_uow as uow:
        assert uow.residents.list_by_apartment(apartment.id) == [resident]
        assert uow.saunas.get(sauna.id) == sauna
        assert uow.weekly_turns.get_by_apartment(apartment.id) == turn
        assert uow.weekly_turns.get_by_slot(sauna.id, 4, time(18)) == turn
        assert uow.bookings.get_by_slot(sauna.id, starts) == booking
        week = (starts - timedelta(days=3), starts + timedelta(days=3))
        assert uow.bookings.list_by_sauna(sauna.id, *week) == [booking]
        assert uow.bookings.list_by_apartment(apartment.id, *week) == [booking]
        later = starts + timedelta(hours=1)
        assert uow.bookings.list_by_apartment(apartment.id, later, week[1]) == []


def test_double_booking_raises_conflict() -> None:
    uow = make_sql_uow()
    apartment = Apartment(number="A 1")
    sauna = Sauna(name="Lower", opens_at=time(17), closes_at=time(22))
    starts = datetime(2026, 11, 20, 19, tzinfo=UTC)
    with uow:
        uow.apartments.add(apartment)
        uow.saunas.add(sauna)
        uow.commit()
    with uow:
        uow.bookings.add(Booking(sauna.id, apartment.id, starts, sauna.turn_end(starts)))
        uow.commit()
    with uow:
        uow.bookings.add(Booking(sauna.id, apartment.id, starts, sauna.turn_end(starts)))
        with pytest.raises(ConflictError):
            uow.commit()
