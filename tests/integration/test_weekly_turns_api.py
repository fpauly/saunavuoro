"""API tests for /weekly-turns: real FastAPI app, in-memory storage."""

from uuid import uuid4

from fastapi.testclient import TestClient

from saunavuoro.api.app import create_app
from saunavuoro.infrastructure.clock import SystemClock
from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork

URL = "/api/v1/weekly-turns"


def make_client() -> TestClient:
    uow = InMemoryUnitOfWork()
    return TestClient(create_app(uow_factory=lambda: uow, clock=SystemClock()))


def create_sauna(client: TestClient) -> str:
    body = {"name": "Lower sauna", "opens_at": "17:00", "closes_at": "22:00"}
    sauna_id: str = client.post("/api/v1/saunas", json=body).json()["id"]
    return sauna_id


def create_apartment(client: TestClient, number: str) -> str:
    apartment_id: str = client.post("/api/v1/apartments", json={"number": number}).json()["id"]
    return apartment_id


def turn(
    sauna_id: str, apartment_id: str, weekday: int = 4, start: str = "18:00"
) -> dict[str, object]:
    return {
        "sauna_id": sauna_id,
        "apartment_id": apartment_id,
        "weekday": weekday,
        "start_time": start,
    }


def test_crud_flow() -> None:
    client = make_client()
    sauna_id = create_sauna(client)
    apartment_id = create_apartment(client, "A 1")

    created = client.post(URL, json=turn(sauna_id, apartment_id))
    assert created.status_code == 201
    turn_id = created.json()["id"]
    assert created.json()["start_time"] == "18:00:00"

    assert client.get(f"{URL}/{turn_id}").json()["weekday"] == 4
    assert [t["id"] for t in client.get(URL, params={"sauna_id": sauna_id}).json()] == [turn_id]
    by_apartment = client.get(URL, params={"apartment_id": apartment_id}).json()
    assert [t["id"] for t in by_apartment] == [turn_id]

    updated = client.put(f"{URL}/{turn_id}", json=turn(sauna_id, apartment_id, 5, "20:00"))
    assert updated.status_code == 200
    assert (updated.json()["weekday"], updated.json()["start_time"]) == (5, "20:00:00")

    assert client.delete(f"{URL}/{turn_id}").status_code == 204
    assert client.get(f"{URL}/{turn_id}").status_code == 404


def test_taken_slot_returns_409() -> None:
    client = make_client()
    sauna_id = create_sauna(client)
    client.post(URL, json=turn(sauna_id, create_apartment(client, "A 1")))

    response = client.post(URL, json=turn(sauna_id, create_apartment(client, "A 2")))

    assert response.status_code == 409
    assert "Fridays at 18:00" in response.json()["detail"]


def test_second_turn_for_the_same_apartment_returns_409() -> None:
    client = make_client()
    sauna_id = create_sauna(client)
    apartment_id = create_apartment(client, "A 1")
    client.post(URL, json=turn(sauna_id, apartment_id))

    response = client.post(URL, json=turn(sauna_id, apartment_id, weekday=5))

    assert response.status_code == 409


def test_start_time_outside_the_turn_grid_returns_422() -> None:
    client = make_client()
    sauna_id = create_sauna(client)
    response = client.post(URL, json=turn(sauna_id, create_apartment(client, "A 1"), start="18:30"))
    assert response.status_code == 422
    assert "must start at one of" in response.json()["detail"]


def test_invalid_weekday_returns_422() -> None:
    client = make_client()
    sauna_id = create_sauna(client)
    response = client.post(URL, json=turn(sauna_id, create_apartment(client, "A 1"), weekday=7))
    assert response.status_code == 422


def test_unknown_sauna_returns_404() -> None:
    client = make_client()
    response = client.post(URL, json=turn(str(uuid4()), create_apartment(client, "A 1")))
    assert response.status_code == 404
