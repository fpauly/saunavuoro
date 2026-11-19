"""API tests for /saunas: real FastAPI app, in-memory storage."""

import pytest
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


def test_administrator_can_set_and_update_booking_rules() -> None:
    client = make_client()
    rules = {
        "turn_length_minutes": 90,
        "max_extra_bookings_per_week": 3,
        "max_days_ahead": 30,
        "cancellation_deadline_hours": 4,
    }

    created = client.post(URL, json=SAUNA | rules)
    assert created.status_code == 201
    body = created.json()
    assert {name: body[name] for name in rules} == rules

    sauna_id = body["id"]
    new_rules = {
        "turn_length_minutes": 30,
        "max_extra_bookings_per_week": 0,
        "max_days_ahead": 7,
        "cancellation_deadline_hours": 1,
    }
    updated = client.put(f"{URL}/{sauna_id}", json=SAUNA | new_rules)
    assert updated.status_code == 200
    assert {name: updated.json()[name] for name in new_rules} == new_rules


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("turn_length_minutes", 0),
        ("max_extra_bookings_per_week", -1),
        ("max_days_ahead", -1),
        ("cancellation_deadline_hours", -1),
    ],
)
def test_invalid_booking_rules_return_422(field: str, value: int) -> None:
    response = make_client().post(URL, json=SAUNA | {field: value})
    assert response.status_code == 422
