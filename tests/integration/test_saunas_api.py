"""API tests for /saunas: real FastAPI app, in-memory storage."""

from fastapi.testclient import TestClient

from saunavuoro.api.app import create_app
from saunavuoro.infrastructure.clock import SystemClock
from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork

URL = "/api/v1/saunas"
SAUNA = {
    "name": "Lower sauna",
    "opens_at": "17:00",
    "closes_at": "22:00",
}


def make_client() -> TestClient:
    uow = InMemoryUnitOfWork()
    return TestClient(create_app(uow_factory=lambda: uow, clock=SystemClock()))


def test_crud_flow() -> None:
    client = make_client()

    created = client.post(URL, json=SAUNA)
    assert created.status_code == 201
    sauna_id = created.json()["id"]
    assert created.json()["turn_length_minutes"] == 60

    assert client.get(f"{URL}/{sauna_id}").json()["name"] == "Lower sauna"
    assert [s["name"] for s in client.get(URL).json()] == ["Lower sauna"]

    updated = client.put(
        f"{URL}/{sauna_id}",
        json=SAUNA | {"name": "Upper sauna", "opens_at": "18:00", "closes_at": "21:00"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Upper sauna"
    assert updated.json()["opens_at"] == "18:00:00"

    assert client.delete(f"{URL}/{sauna_id}").status_code == 204
    assert client.get(f"{URL}/{sauna_id}").status_code == 404


def test_invalid_opening_hours_return_422() -> None:
    client = make_client()
    response = client.post(URL, json=SAUNA | {"closes_at": "16:00"})
    assert response.status_code == 422
