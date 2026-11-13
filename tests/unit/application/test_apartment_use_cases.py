"""Use case tests: the in-memory UnitOfWork replaces the database."""

from uuid import uuid4

import pytest

from saunavuoro.application.errors import AlreadyExistsError, NotFoundError
from saunavuoro.application.use_cases.apartments import (
    CreateApartment,
    DeleteApartment,
    GetApartment,
    UpdateApartment,
)
from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork


def test_create_apartment_saves_and_commits(uow: InMemoryUnitOfWork) -> None:
    apartment = CreateApartment(uow).execute("A 1")

    assert uow.apartments.get(apartment.id) == apartment
    assert uow.committed


def test_duplicate_number_is_rejected(uow: InMemoryUnitOfWork) -> None:
    CreateApartment(uow).execute("A 1")

    with pytest.raises(AlreadyExistsError):
        CreateApartment(uow).execute("a 1")


def test_update_changes_number(uow: InMemoryUnitOfWork) -> None:
    apartment = CreateApartment(uow).execute("A 1")

    UpdateApartment(uow).execute(apartment.id, "B 2")

    assert GetApartment(uow).execute(apartment.id).number == "B 2"


def test_get_unknown_apartment_raises_not_found(uow: InMemoryUnitOfWork) -> None:
    with pytest.raises(NotFoundError):
        GetApartment(uow).execute(uuid4())


def test_delete_apartment(uow: InMemoryUnitOfWork) -> None:
    apartment = CreateApartment(uow).execute("A 1")

    DeleteApartment(uow).execute(apartment.id)

    assert uow.apartments.get(apartment.id) is None
