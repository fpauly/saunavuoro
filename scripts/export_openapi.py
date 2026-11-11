"""Write the OpenAPI specification to docs/openapi.json.

Run from the project root: python scripts/export_openapi.py
No database is needed.
"""

import json
from pathlib import Path

from saunavuoro.api.app import create_app
from saunavuoro.infrastructure.clock import SystemClock
from saunavuoro.infrastructure.persistence.in_memory import InMemoryUnitOfWork

OUTPUT = Path(__file__).resolve().parent.parent / "docs" / "openapi.json"


def main() -> None:
    spec = create_app(uow_factory=InMemoryUnitOfWork, clock=SystemClock()).openapi()
    OUTPUT.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
