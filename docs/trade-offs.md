# Trade-off Analysis

This document summarises the main architectural decisions of SaunaVuoro, the alternatives we considered, and what each decision costs. The individual decisions are described in more detail in the Architecture Decision Records in `docs/adr/`.

## 1. Quality attributes that drive the design

The topic proposal names three priority quality attributes: **maintainability**, **testability** and **data integrity**. The value of the system lies in correctly enforced booking rules (no double bookings, opening hours, weekly limits, booking and cancellation deadlines), and these rules are expected to change. Supporting attributes are extensibility, API usability, robustness and type safety.

When two attributes conflicted, we preferred the priority attributes over development speed and the amount of code. The table below shows where this happened.

| Decision | Quality gained | Quality given up |
| -------- | -------------- | ---------------- |
| Clean Architecture with four layers ([ADR 0001](adr/0001-use-clean-architecture.md)) | Maintainability, testability | Development speed, simplicity |
| Database constraints + unit of work ([ADR 0002](adr/0002-prevent-double-bookings-with-database-constraints.md)) | Data integrity | Flexibility of the time grid; generic conflict messages |
| Typed exceptions instead of result types ([ADR 0003](adr/0003-use-exceptions-for-errors.md)) | Simplicity, readable use cases | Errors are not visible in function signatures |
| FastAPI + PostgreSQL + SQLAlchemy ([ADR 0004](adr/0004-use-fastapi-and-postgresql.md)) | API usability, type safety, integrity | Extra mapping code; framework-specific DI |
| Injected clock, local time rules, UTC storage ([ADR 0005](adr/0005-time-handling.md)) | Testability, correctness across daylight saving changes | Time zone conversions |
| Booking rules as components ([ADR 0006](adr/0006-booking-rules-as-components.md)) | Extensibility (Open/Closed) | More classes; one shared context object |

## 2. Clean Architecture: benefits and drawbacks for this project

The main decision was to use Clean Architecture instead of a layered FastAPI application where routers call the database directly. We evaluated it against our experience of building the project so far.

### Benefits we have seen

- **Business rules are tested without infrastructure.** Domain and use case tests (`tests/unit/`) run with `InMemoryUnitOfWork` and need no database or web server. The whole test suite runs without Docker.
- **The same tests run against two implementations.** `tests/integration/test_repositories.py` runs each repository test with both the SQL and the in-memory unit of work (`any_uow` fixture). This shows that the in-memory implementation behaves like the real one, so the unit tests can be trusted.
- **A fixed recipe for new features.** `docs/design.md` describes how to add a feature, layer by layer, using `Apartment` as the model. Residents, saunas and bookings were implemented by different team members following the same structure, which made parallel work and code review easier.
- **Clear place for every piece of code.** Validation of a sauna's opening hours lives in `domain/sauna.py`, uniqueness checks in the use cases, HTTP status codes in `api/errors.py`, and SQL in the repositories. Nobody had to discuss where code should go.
- **Replaceable infrastructure.** The database, the clock and the web framework are chosen only in `main.py`. Switching from PostgreSQL to SQLite in tests needed no change to the application code.
- **SOLID is visible in the code.** The repository and clock ports apply the Dependency Inversion Principle; one class per use case applies the Single Responsibility Principle; booking rule components apply the Open/Closed Principle.

### Drawbacks we have seen

- **More code for simple features.** Apartment CRUD needs an entity, five use case classes, a port, a SQL repository, an in-memory repository, an ORM model, two Pydantic schemas and a router. A plain FastAPI app would need a model, a schema and a router. For the CRUD part of the system, Clean Architecture is mostly overhead.
- **Data is converted twice.** ORM model ↔ entity in the repositories, and entity ↔ Pydantic schema in the API layer. Each new field must be added in four places (entity, ORM model, schema, migration).
- **Two repository implementations to maintain.** Every new repository method must be written for both SQL and in-memory, and the in-memory version can drift from the real behaviour. The shared integration tests reduce this risk, but only for methods that are tested.
- **Steeper start for the team.** Ports, `Protocol`, the unit of work and the composition root were new to some members. The first feature took longer than it would have in a simple layered app.
- **The dependency rule is checked only by review.** Nothing stops a developer from importing SQLAlchemy in a use case. A tool such as `import-linter` could check this in CI.

### Evaluation

For the CRUD resources (apartments, residents) Clean Architecture costs more than it gives. For the booking part, where the rules are complex, time-dependent and expected to change, it pays off: the rules can be tested quickly and in isolation, and new rules can be added without touching the infrastructure. Since booking is the core of the system, we consider the choice justified. In a real product we might use a simpler structure for the CRUD resources and keep the layers only for the booking logic. The course requires explicit layers, so we used them everywhere for consistency.

## 3. Key trade-offs in detail

### 3.1 Where integrity is enforced

Checking rules only in the use cases leaves a race condition: two parallel requests can both see a turn as free. Locking the sauna row (`SELECT … FOR UPDATE`) would solve this for every rule, but it adds locking code to the repositories and serialises requests. A PostgreSQL exclusion constraint would prevent any time overlap, but it needs an extension and cannot be tested on SQLite.

We chose unique constraints on `(sauna_id, starts_at)` and `(sauna_id, weekday, start_time)`, which are enough because turns are on a fixed time grid. The unit of work translates a constraint error into `ConflictError` (`409`). The cost is that integrity depends on the grid not changing while bookings exist, and the weekly booking limit is checked only in code. We accept this because a broken weekly limit means one extra booking, while a double booking means two households at the sauna at the same time.

### 3.2 Exceptions or result types

Result types make errors part of a function's type and let mypy check that they are handled. In Python this means writing or importing a `Result` type and unwrapping it in every use case and router. We chose typed exceptions mapped to HTTP codes in one place (`api/errors.py`), because this is the normal Python and FastAPI style and keeps the use cases short. The cost is that a use case's possible errors are found in the tests and the `error_responses(...)` list, not in its signature.

### 3.3 Code-first or design-first API

Design-first (write the OpenAPI file, then the code) would let the team agree on the contract before implementing. We chose code-first because FastAPI generates the specification from the type hints, so the documentation cannot drift from the code. A test checks that the exported `docs/openapi.json` is up to date. The cost is that the contract is visible only after the endpoint is written; we discuss endpoints in pull requests instead.

### 3.4 Testing strategy

| Test type | What it uses | What it proves | Speed |
| --------- | ------------ | -------------- | ----- |
| Domain unit tests | Entities only | Business rules | Fastest |
| Use case unit tests | `InMemoryUnitOfWork`, `FixedClock` | Application logic, error cases | Fast |
| Repository integration tests | SQLite and in-memory unit of work | Mapping, constraints, both implementations agree | Fast |
| API integration tests | `TestClient` + in-memory unit of work | Routing, validation, status codes, error format | Fast |

The trade-off is that no automatic test runs against PostgreSQL. SQLite does not behave exactly like PostgreSQL (for example, it returns naive datetimes and handles concurrency differently). We accepted this to keep the test suite free of Docker; PostgreSQL behaviour is checked manually with the Docker Compose database before the demo.

## 4. Risks and future work

- **Changing a sauna's turn grid** while future bookings exist could allow overlapping bookings. The update-sauna use case should reject this, or we should add an exclusion constraint.
- **Weekly limit under concurrency** is not guaranteed by the database. Row locking on the apartment could close this gap if needed.
- **No authentication.** Residents are identified only by apartment ID in the request. Adding authentication would affect the API layer and add a "current apartment" port, but not the domain.
- **Automatic check of the dependency rule** with `import-linter` would make the architecture enforceable instead of a convention.
