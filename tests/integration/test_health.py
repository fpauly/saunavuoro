"""Health check endpoint used by development tools."""

from fastapi.testclient import TestClient

from saunavuoro.api.app import create_app
from saunavuoro.infrastructure.clock import SystemClock
from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork


def make_client() -> TestClient:
    uow = InMemoryUnitOfWork()
    return TestClient(create_app(uow_factory=lambda: uow, clock=SystemClock()))


def test_health_returns_ok() -> None:
    response = make_client().get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_is_not_part_of_the_public_api() -> None:
    spec = create_app(uow_factory=InMemoryUnitOfWork, clock=SystemClock()).openapi()

    assert "/health" not in spec["paths"]
