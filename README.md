# SaunaVuoro

A backend application for booking sauna turns in a Finnish apartment building, built for the Software Architecture course (autumn 2026).

> **Status:** Early development. The architecture skeleton is in place, with administrator CRUD for apartments, residents and saunas implemented.

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
- pytest, mypy (strict), ruff
- Docker Compose (database)

## Repository Structure

```text
saunavuoro/
├── src/saunavuoro/
│   ├── domain/           # entities, business rules, errors
│   ├── application/      # use cases and ports (interfaces)
│   ├── api/              # FastAPI app, routers, schemas, error mapping
│   ├── infrastructure/   # database models, repositories, config
│   └── main.py           # composition root
├── migrations/           # Alembic migrations
├── scripts/              # export_openapi.py
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── adr/            # Architecture Decision Records
│   ├── diagrams/
│   ├── openapi.json    # exported API specification
│   └── ai-usage.md     # AI usage log
└── README.md
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Setup

```bash
cp .env.example .env              # adjust DB_PORT / DATABASE_URL if port 5432 is taken
docker compose up -d              # start PostgreSQL
export $(grep -v '^#' .env | xargs)   # load the variables into the shell
alembic upgrade head              # create the tables
```

## Running the Application

```bash
uvicorn saunavuoro.main:app --reload
```

## API Access

Once running:

| URL                                   | Content                                  |
| ------------------------------------- | ---------------------------------------- |
| `http://localhost:8000/docs`          | Swagger UI – try the API in the browser  |
| `http://localhost:8000/redoc`         | ReDoc – read-only API documentation      |
| `http://localhost:8000/openapi.json`  | OpenAPI 3.1 specification                |

All endpoints are under `/api/v1`.

| Resource   | Endpoints                                                                 |
| ---------- | ------------------------------------------------------------------------- |
| Apartments | `POST/GET /apartments`, `GET/PUT/DELETE /apartments/{id}`                 |
| Residents  | `POST/GET /residents` (`?apartment_id=` filter), `GET/PUT/DELETE /residents/{id}` |
| Saunas     | `POST/GET /saunas`, `GET/PUT/DELETE /saunas/{id}`                         |

Rules:

- Apartment numbers are unique.
- A resident must belong to an existing apartment.
- Missing resources return `404`; invalid input returns `422`; conflicting data returns `409`.

A copy of the specification is stored in `docs/openapi.json`. Update it after changing the API:

```bash
python scripts/export_openapi.py
```

## Running Tests

```bash
pytest          # unit + integration tests (no database needed)
mypy            # strict type checking
```

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
- Weekly turns and one-off bookings are not implemented yet.

## Team

- Fan Yin
