# ADR 0003: Report errors with typed exceptions mapped to HTTP status codes

- **Status:** Accepted
- **Date:** 2026-11-28

## Context

Every use case can fail in a few expected ways: a resource does not exist, the data conflicts with existing data, or a business rule is broken (for example a turn outside opening hours). The API must answer these with the correct 4xx status code and a message that says which rule was broken (topic proposal, robustness requirement). The application layer must not know about HTTP, and the routers must not contain business logic.

The two common ways to report expected errors are exceptions and result types (a return value that is either a success or an error, such as `Result[Booking, BookingError]`).

## Decision

We use **typed exceptions**, grouped by layer:

| Exception | Layer | Meaning | HTTP |
| --------- | ----- | ------- | ---- |
| `DomainError` → `RuleViolationError`, `InvalidApartmentNumberError` | domain | A business rule is broken | 422 |
| `NotFoundError(resource, id)` | application | The resource does not exist | 404 |
| `ConflictError`, `AlreadyExistsError` | application | The change conflicts with existing data | 409 |

The domain raises errors from entity constructors and methods (`Sauna.__post_init__`). Use cases raise application errors. One translation table in the API layer (`api/errors.py`) maps the exception types to status codes, and every error is returned in the same JSON format, `{"detail": "..."}` (`ErrorResponse`). An unmapped `DomainError` defaults to `422`. Each endpoint lists its possible errors with `responses=error_responses(...)`, so they also appear in Swagger UI.

Request validation (wrong types, missing fields) is done by Pydantic in the API schemas and returns FastAPI's standard `422`.

## Alternatives considered

| Option | Pros | Cons |
| ------ | ---- | ---- |
| **Result types** (`Ok` / `Err` return values) | Errors are part of the function signature, and mypy forces the caller to handle them | Python has no built-in result type or pattern for it; every use case and router must unwrap results; more code for the same behaviour; unusual for FastAPI |
| **`HTTPException` raised in use cases** | Very little code | The application layer would depend on FastAPI and HTTP, which breaks the dependency rule |
| **Typed exceptions + one mapping in the API layer** (chosen) | Idiomatic Python; use cases stay short; HTTP knowledge is in one file; adding an error type is one line in the mapping | Errors are not visible in function signatures; a missing handler gives `500` instead of a compile-time error |

## Consequences

- **Positive:** Domain and application code has no HTTP or FastAPI imports. Unit tests check errors with `pytest.raises(RuleViolationError)`.
- **Positive:** The error format is consistent across the API, and the error responses are documented in OpenAPI.
- **Negative:** Readers must look at the docstrings or tests to see which errors a use case raises. We reduce this risk with the `error_responses(...)` list on every endpoint and API tests for each error status.
- **Negative:** Unexpected exceptions (bugs, a lost database connection) are not mapped and return `500`. This is intended: they are not expected errors and should not be hidden as 4xx responses.
