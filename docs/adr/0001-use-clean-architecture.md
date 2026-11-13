# ADR 0001: Use Clean Architecture

- **Status:** Accepted
- **Date:** 2026-11-09

## Context

SaunaVuoro's value is in its booking rules (no overlapping turns, weekly limits, opening hours), and these rules will change during the project. The course requires API, Application, Domain and Infrastructure layers, and our most important quality attributes are maintainability, testability and data integrity (see the topic proposal). We want to test the rules without a database or a web server.

## Decision

We split the code into four layers – `domain`, `application`, `api` and `infrastructure` – and source code dependencies point inward only. Use cases depend on interfaces (ports, written as `typing.Protocol`); the infrastructure layer implements them. Concrete classes are chosen only in the composition root, `src/saunavuoro/main.py`, and passed in with Dependency Injection.

## Alternatives considered

| Option | Pros | Cons |
| ------ | ---- | ---- |
| **Layered (MVC-style) FastAPI app** – routers call SQLAlchemy directly | Less code, fast to start, familiar | Business rules end up in routers or ORM code; hard to test without a database; does not meet the course requirements |
| **Clean Architecture** (chosen) | Rules are isolated and easy to unit test; database and framework can be replaced; clear place for every piece of code | More files and mapping code (ORM model ↔ entity ↔ API schema); steeper start for the team |
| **Vertical slices** – one folder per feature with everything inside | Feature code is kept together | Layer boundaries are less visible; the course asks for explicit layers |

## Consequences

- **Positive:** Domain and use case tests run in milliseconds with in-memory repositories. Adding a feature follows a fixed recipe (see `docs/design.md`), which helps four people work in parallel.
- **Negative:** Every feature needs code in several layers, and data is converted twice. For a simple CRUD resource such as `Apartment` this is more work than a plain FastAPI app.
- **Follow-up:** The dependency rule is not yet checked automatically; a tool such as `import-linter` could be added later.
