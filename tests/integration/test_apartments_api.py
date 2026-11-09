"""API tests: real FastAPI app, in-memory storage."""

from fastapi.testclient import TestClient

from saunavuoro.api.app import create_app
from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork

URL = "/api/v1/apartments"


def make_client() -> TestClient:
    uow = InMemoryUnitOfWork()
    return TestClient(create_app(uow_factory=lambda: uow))


def test_crud_flow() -> None:
    client = make_client()

    created = client.post(URL, json={"number": "A 1"})
    assert created.status_code == 201
    apartment_id = created.json()["id"]

    assert client.get(f"{URL}/{apartment_id}").json()["number"] == "A 1"
    assert client.put(f"{URL}/{apartment_id}", json={"number": "B 2"}).status_code == 200
    assert [a["number"] for a in client.get(URL).json()] == ["B 2"]
    assert client.delete(f"{URL}/{apartment_id}").status_code == 204
    assert client.get(f"{URL}/{apartment_id}").status_code == 404


def test_duplicate_returns_409() -> None:
    client = make_client()
    client.post(URL, json={"number": "A 1"})
    assert client.post(URL, json={"number": "A 1"}).status_code == 409


def test_blank_number_returns_422() -> None:
    assert make_client().post(URL, json={"number": "   "}).status_code == 422
