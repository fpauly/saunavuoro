"""Repository tests against a real SQL database (SQLite in memory)."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from saunavuoro.domain.apartment import Apartment
from saunavuoro.infrastructure.persistence import models  # noqa: F401  (registers tables)
from saunavuoro.infrastructure.persistence.database import Base
from saunavuoro.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork


def make_uow() -> SqlAlchemyUnitOfWork:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    return SqlAlchemyUnitOfWork(sessionmaker(bind=engine, expire_on_commit=False))


def test_saved_apartment_can_be_loaded() -> None:
    uow = make_uow()
    apartment = Apartment(number="A 1")
    with uow:
        uow.apartments.add(apartment)
        uow.commit()

    with uow:
        assert uow.apartments.get(apartment.id) == apartment
        assert uow.apartments.get_by_number("A 1") == apartment


def test_without_commit_nothing_is_saved() -> None:
    uow = make_uow()
    with uow:
        uow.apartments.add(Apartment(number="A 1"))

    with uow:
        assert uow.apartments.list_all() == []
