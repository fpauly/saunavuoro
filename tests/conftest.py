import pytest

from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()
