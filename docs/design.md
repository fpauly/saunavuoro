# Architecture and Design

## Layers and the dependency rule

```text
              main.py  (composition root: chooses implementations, wires everything)
                 |
       +---------+----------+
       v                    v
      api             infrastructure
  (FastAPI routers,    (SQLAlchemy models, repositories,
   schemas)             unit of work, config)
       |                    |   implements the ports
       +---------+----------+
                 v
            application
       (use cases + ports)
                 |
                 v
              domain
   (entities, business rules, errors)
```

Source code dependencies point **inward only**:

| Layer          | May import                  | Must not import                                 |
| -------------- | --------------------------- | ----------------------------------------------- |
| domain         | standard library only       | application, api, infrastructure, any framework |
| application    | domain                      | api, infrastructure, FastAPI, SQLAlchemy        |
| infrastructure | application (ports), domain | api                                             |
| api            | application, domain         | infrastructure                                  |
| `main.py`      | everything                  | –                                               |

## Example feature: Apartment

`Apartment` is implemented through every layer and is the model for all other features.

| Layer          | File                                                    | What it does                                             |
| -------------- | ------------------------------------------------------- | -------------------------------------------------------- |
| domain         | `domain/apartment.py`, `domain/errors.py`               | Entity and its rule (number not empty, max 20 chars)     |
| application    | `application/ports.py`                                  | `ApartmentRepository` interface, `UnitOfWork`            |
| application    | `application/use_cases/apartments.py`                   | Create, Get, List, Update, Delete (one class per use case) |
| infrastructure | `infrastructure/persistence/models.py`                  | `ApartmentModel` (database table)                        |
| infrastructure | `infrastructure/persistence/apartment_repository.py`    | SQLAlchemy repository, converts model ↔ entity           |
| infrastructure | `infrastructure/persistence/in_memory.py`               | In-memory repository for tests                           |
| infrastructure | `infrastructure/persistence/unit_of_work.py`            | Transaction: commit or roll back                         |
| api            | `api/schemas/apartments.py`                             | Request/response models, entity → response               |
| api            | `api/routers/apartments.py`                             | `/api/v1/apartments` endpoints, calls use cases only     |
| api            | `api/errors.py`                                         | Errors → HTTP status (404, 409, 422)                     |
| api            | `api/schemas/errors.py`                                 | Error response models + `error_responses()` for OpenAPI  |
| migrations     | `migrations/versions/0001_create_apartments.py`         | Creates the table                                        |

### Request flow: `POST /api/v1/apartments`

1. The router validates the JSON body with `ApartmentIn`.
2. The router calls `CreateApartment(uow).execute(number)`. The `uow` is injected (Dependency Injection); the router does not know it is SQLAlchemy.
3. The use case creates an `Apartment` (the domain checks the number), checks that the number is unique and saves it through the repository port, then commits.
4. The router converts the entity to `ApartmentOut` and returns `201`. If an error is raised, `api/errors.py` turns it into `404`, `409` or `422`.

## How to add a new feature (copy the Apartment example)

Example: adding `Sauna`.

1. **Domain** – `domain/sauna.py`: the entity and its rules. Add new errors to `domain/errors.py`.
2. **Port** – `application/ports.py`: add `SaunaRepository(Protocol)` and a `saunas` property in `UnitOfWork`.
3. **Use cases** – `application/use_cases/saunas.py`: one class per use case.
4. **ORM model** – `infrastructure/persistence/models.py`: add `SaunaModel`.
5. **Repository** – `infrastructure/persistence/sauna_repository.py`; register it in `unit_of_work.py` (`self.saunas = ...`).
6. **In-memory repository** – add `InMemorySaunaRepository` to `in_memory.py` and to `InMemoryUnitOfWork`.
7. **Migration** – `alembic revision --autogenerate -m "create saunas table"` (database must be running), then check the generated file.
8. **API** – `api/schemas/saunas.py`, `api/routers/saunas.py`, and include the router in `api/app.py`. Map new errors in `api/errors.py` if they need a status other than 422.
   - Give every endpoint a `summary=`, a docstring (shown as the description in Swagger UI) and `responses=error_responses(...)` listing the error codes it can return.
   - Add a `Field(description=..., examples=[...])` to schema fields.
   - Add the new tag to `TAGS` in `api/app.py`.
9. **Tests** – `tests/unit/domain/`, `tests/unit/application/`, `tests/integration/`.
10. Run `python scripts/export_openapi.py` to update `docs/openapi.json`, then `pytest` and `mypy` before committing.

## API documentation (OpenAPI)

FastAPI generates an OpenAPI 3.1 specification from the code (code-first). It is served at `/openapi.json` and shown by Swagger UI (`/docs`) and ReDoc (`/redoc`). A copy is kept in `docs/openapi.json`; a test fails if the copy is out of date.
