# ADR 0004: Use FastAPI with code-first OpenAPI and PostgreSQL with SQLAlchemy

- **Status:** Accepted
- **Date:** 2026-11-28

## Context

The course requires a REST API documented and testable with Swagger/OpenAPI, persistent storage in a database, and database access separated from business logic. Our team knows Python best. We also want static typing checked by mypy in strict mode (topic proposal, type safety requirement).

## Decision

- **Web framework:** FastAPI. The OpenAPI 3.1 specification is generated from the code (code-first) and served at `/openapi.json`, with Swagger UI at `/docs` and ReDoc at `/redoc`. A copy is exported to `docs/openapi.json` by `scripts/export_openapi.py`, and `tests/integration/test_openapi.py` fails if the copy is out of date.
- **Database:** PostgreSQL 16, started with Docker Compose for development.
- **Data access:** SQLAlchemy 2.0 (typed `Mapped[...]` models) behind repository ports. The ORM models are separate from the domain entities and exist only in the infrastructure layer.
- **Schema changes:** Alembic migrations in `migrations/versions/`.

## Alternatives considered

| Option | Pros | Cons |
| ------ | ---- | ---- |
| **Flask + flask-smorest** | Mature and well known | OpenAPI and validation are add-ons; weaker type hints |
| **Django REST Framework** | Many built-in features (admin, auth, ORM) | The ORM and models are the centre of Django; this works against Clean Architecture, where entities must not depend on a framework |
| **Design-first OpenAPI** (write `openapi.yaml`, then generate code) | The contract can be agreed before coding | Specification and code must be kept in sync by hand; more tooling |
| **SQLite as the only database** | No Docker needed | No real concurrency; weaker types for time zones; not what a real deployment would use |
| **SQLAlchemy Core / raw SQL** | Full control over queries | More code to map rows; no unit of work |
| **FastAPI + PostgreSQL + SQLAlchemy ORM** (chosen) | Validation, OpenAPI and Dependency Injection built in; type hints everywhere; reliable transactions and constraints | Two models per resource (ORM model and entity) plus an API schema; FastAPI's `Depends` is a framework-specific DI mechanism |

## Consequences

- **Positive:** Swagger UI is always in sync with the code and is used for testing and the demo.
- **Positive:** Because SQLAlchemy is used only behind ports, the tests can run with `InMemoryUnitOfWork` or SQLite, and the database could be replaced without changing the use cases.
- **Negative:** Data is mapped twice: ORM model ↔ entity in the repositories, and entity ↔ Pydantic schema in the API layer.
- **Negative:** The integration tests run on SQLite, not PostgreSQL, so PostgreSQL-specific behaviour (for example time zone handling of `timestamptz`) is not covered by the automatic tests and must be checked manually against the Docker database.
