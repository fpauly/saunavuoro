"""Checks that the API documentation is generated and up to date."""

import json
from pathlib import Path

from saunavuoro.api.app import create_app
from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork

EXPORTED = Path(__file__).resolve().parents[2] / "docs" / "openapi.json"


def test_error_responses_are_documented() -> None:
    spec = create_app(uow_factory=InMemoryUnitOfWork).openapi()
    post = spec["paths"]["/api/v1/apartments"]["post"]
    assert {"201", "409", "422"} <= set(post["responses"])


def test_exported_openapi_is_up_to_date() -> None:
    spec = create_app(uow_factory=InMemoryUnitOfWork).openapi()
    assert json.loads(EXPORTED.read_text(encoding="utf-8")) == spec, (
        "docs/openapi.json is outdated. Run: python scripts/export_openapi.py"
    )
