"""API tests for /residents: real FastAPI app, in-memory storage."""

from fastapi.testclient import TestClient

from saunavuoro.api.app import create_app
from saunavuoro.infrastructure.clock import SystemClock
from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork

APARTMENTS = "/api/v1/apartments"
URL = "/api/v1/residents"


def make_client() -> TestClient:
    uow = InMemoryUnitOfWork()
    return TestClient(create_app(uow_factory=lambda: uow, clock=SystemClock()))


def make_apartment(client: TestClient, number: str = "A 1") -> str:
    response = client.post(APARTMENTS, json={"number": number})
    assert response.status_code == 201
    return str(response.json()["id"])


def test_crud_flow() -> None:
    client = make_client()
    apartment_id = make_apartment(client)

    created = client.post(URL, json={"apartment_id": apartment_id, "name": "Maija Virtanen"})
    assert created.status_code == 201
    resident_id = created.json()["id"]

    assert client.get(f"{URL}/{resident_id}").json()["name"] == "Maija Virtanen"
    assert [r["name"] for r in client.get(URL).json()] == ["Maija Virtanen"]
    assert [r["name"] for r in client.get(URL, params={"apartment_id": apartment_id}).json()] == [
        "Maija Virtanen"
    ]

    updated = client.put(
        f"{URL}/{resident_id}",
        json={"apartment_id": apartment_id, "name": "Maija Korhonen"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Maija Korhonen"

    assert client.delete(f"{URL}/{resident_id}").status_code == 204
    assert client.get(f"{URL}/{resident_id}").status_code == 404


def test_unknown_apartment_returns_404() -> None:
    client = make_client()
    response = client.post(
        URL,
        json={
            "apartment_id": "00000000-0000-0000-0000-000000000000",
            "name": "Maija Virtanen",
        },
    )
    assert response.status_code == 404


def test_blank_name_returns_422() -> None:
    client = make_client()
    apartment_id = make_apartment(client)
    response = client.post(URL, json={"apartment_id": apartment_id, "name": "   "})
    assert response.status_code == 422
