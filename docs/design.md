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
| infrastructure | `infrastructure/persistence/models.py`                  | `ApartmentModel` and the ORM models of all other tables  |
| infrastructure | `infrastructure/persistence/apartment_repository.py`    | SQLAlchemy repository, converts model ↔ entity           |
| infrastructure | `infrastructure/persistence/in_memory.py`               | In-memory repository for tests                           |
| infrastructure | `infrastructure/persistence/unit_of_work.py`            | Transaction: commit or roll back                         |
| api            | `api/schemas/apartments.py`                             | Request/response models, entity → response               |
| api            | `api/routers/apartments.py`                             | `/api/v1/apartments` endpoints, calls use cases only     |
| api            | `api/errors.py`                                         | Errors → HTTP status (404, 409, 422)                     |
| api            | `api/schemas/errors.py`                                 | Error response models + `error_responses()` for OpenAPI  |
| migrations     | `migrations/versions/0001_create_apartments.py`         | Creates the table                                        |
| migrations     | `migrations/versions/0002_create_remaining_tables.py`   | Creates residents, saunas, weekly_turns, bookings        |

### Request flow: `POST /api/v1/apartments`

1. The router validates the JSON body with `ApartmentIn`.
2. The router calls `CreateApartment(uow).execute(number)`. The `uow` is injected (Dependency Injection); the router does not know it is SQLAlchemy.
3. The use case creates an `Apartment` (the domain checks the number), checks that the number is unique and saves it through the repository port, then commits.
4. The router converts the entity to `ApartmentOut` and returns `201`. If an error is raised, `api/errors.py` turns it into `404`, `409` or `422`.

## Shared foundation (already in place)

Everything below exists for all features, so each feature only adds its own files:

| What                         | Where                                                                 |
| ---------------------------- | --------------------------------------------------------------------- |
| Entities (fields only)       | `domain/resident.py`, `domain/weekly_turn.py`, `domain/booking.py`    |
| Sauna + time grid            | `domain/sauna.py`: `turn_start_times()`, `is_turn_start()`, `turn_end()` |
| Repository ports, `Clock`    | `application/ports.py`                                                |
| SQL repositories             | `infrastructure/persistence/*_repository.py`, all in `unit_of_work.py` |
| In-memory repositories       | `infrastructure/persistence/in_memory.py`                             |
| Clock                        | `infrastructure/clock.py`: `SystemClock` (Europe/Helsinki), `FixedClock` for tests |
| Empty routers                | `api/routers/{residents,saunas,weekly_turns,bookings}.py`, included in `api/app.py` |

Errors:

| Raise                                   | Layer       | HTTP |
| --------------------------------------- | ----------- | ---- |
| `RuleViolationError("...")`             | domain      | 422  |
| `NotFoundError(resource, id)`           | application | 404  |
| `ConflictError("...")`, `AlreadyExistsError` | application | 409  |

A database constraint error on `commit()` (for example two bookings of the same turn, or deleting
a sauna that still has bookings) is turned into `ConflictError` by the unit of work.

Times: `Clock.now()` returns an aware datetime in Europe/Helsinki. Use cases get the clock as a
constructor argument; routers get it with the `CurrentClock` dependency. Bookings are stored as UTC.

## How to add a feature (copy the Apartment example)

Example: `Sauna`.

1. **Domain** – add the rules to the entity (`domain/sauna.py`). Raise `RuleViolationError`.
2. **Use cases** – `application/use_cases/saunas.py`: one class per use case.
3. **API** – `api/schemas/saunas.py`, and the endpoints in `api/routers/saunas.py`.
   - Give every endpoint a `summary=`, a docstring (shown as the description in Swagger UI) and `responses=error_responses(...)` listing the error codes it can return.
   - Add a `Field(description=..., examples=[...])` to schema fields.
4. **Tests** – `tests/unit/domain/`, `tests/unit/application/`, `tests/integration/`.
5. If a repository method is missing, add it to the port in `application/ports.py`, the SQL
   repository and the in-memory repository.
6. Only if you change a table: `alembic revision --autogenerate -m "..."` (database must be running), then check the generated file.
7. Run `python scripts/export_openapi.py` to update `docs/openapi.json`, then `pytest` and `mypy` before committing.

## API documentation (OpenAPI)

FastAPI generates an OpenAPI 3.1 specification from the code (code-first). It is served at `/openapi.json` and shown by Swagger UI (`/docs`) and ReDoc (`/redoc`). A copy is kept in `docs/openapi.json`; a test fails if the copy is out of date.
