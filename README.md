# SaunaVuoro

A backend application for booking sauna turns in a Finnish apartment building, built for the Software Architecture course (autumn 2026).

> **Status:** Early development. Sections marked _TBD_ will be completed as the project progresses.

## Project Overview

Many Finnish apartment buildings have a shared sauna that residents use in turns (_saunavuoro_). Each apartment can have a weekly fixed turn, and free hours can be booked separately.

SaunaVuoro provides a REST API for managing apartments, residents, saunas, weekly turns and one-off bookings. The application enforces the building's booking rules, such as preventing overlapping turns and limiting the number of bookings per week.

The project follows **Clean Architecture**, with the code split into four layers:

| Layer          | Folder                          | Responsibility                              |
| -------------- | ------------------------------- | ------------------------------------------- |
| Domain         | `src/saunavuoro/domain`         | Entities, value objects and business rules  |
| Application    | `src/saunavuoro/application`    | Use cases and interfaces (ports)            |
| API            | `src/saunavuoro/api`            | REST endpoints and request/response models  |
| Infrastructure | `src/saunavuoro/infrastructure` | Database access and other external concerns |

## Technology

- Python 3.12, FastAPI
- PostgreSQL, SQLAlchemy, Alembic
- pytest, mypy (strict)
- Docker Compose (database)

## Repository Structure

```text
saunavuoro/
├── src/saunavuoro/
│   ├── domain/
│   ├── application/
│   ├── api/
│   └── infrastructure/
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── adr/            # Architecture Decision Records
│   ├── diagrams/
│   └── ai-usage.md     # AI usage log
└── README.md
```

## Installation

_TBD_

## Setup

_TBD_ (database with Docker Compose, environment variables, migrations)

## Running the Application

_TBD_

## API Access

Once running, the interactive Swagger UI will be available at `http://localhost:8000/docs`.

## Running Tests

_TBD_

## Documentation

- Architecture and design: `docs/design.md`
- Architecture decisions: `docs/adr/`
- AI usage: `docs/ai-usage.md`

## Assumptions

- The system serves a single apartment building with one or more saunas.
- Sauna turns are one hour long and start on the full hour.
- All times are in the Europe/Helsinki time zone.

## Limitations

- Backend only; no frontend. Swagger UI is used for testing and demonstration.
- No authentication or authorisation.
- No payments or notifications.

## Team

- [Fan Yin]
