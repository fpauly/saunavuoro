# SaunaVuoro

A backend application for booking sauna turns in a Finnish apartment building, built for the Software Architecture course (autumn 2026).

SaunaVuoro provides a REST API for managing apartments, residents, saunas, weekly turns and one-off bookings. The current milestone implements administrator CRUD for apartments, residents and saunas.

## Technology

- Python 3.12+ (tested on Python 3.14), FastAPI
- PostgreSQL, SQLAlchemy, Alembic
- Docker Compose (database)

## Repository Structure

```text
saunavuoro/
├── src/saunavuoro/
│   ├── domain/           # Entities and business rules
│   ├── application/      # Use cases and repository interfaces
│   ├── api/              # FastAPI app, routers and schemas
│   └── infrastructure/   # Settings, database models and repositories
├── migrations/           # Alembic migrations
├── compose.yaml          # PostgreSQL for local development
├── alembic.ini
└── pyproject.toml
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

## Setup

Start PostgreSQL and apply the migration:

```powershell
docker compose up -d db
.\.venv\Scripts\alembic.exe upgrade head
```

The database listens on host port **5434** to avoid clashing with other local PostgreSQL instances. Credentials and the connection URL are in `compose.yaml` and `.env.example`.

## Running the Application

```powershell
.\.venv\Scripts\uvicorn.exe saunavuoro.api.main:app --reload
```

- Swagger UI: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

## API

All endpoints are under `/api/v1`.

| Resource   | Endpoints                                                                 |
| ---------- | ------------------------------------------------------------------------- |
| Apartments | `POST/GET /apartments`, `GET/PUT/DELETE /apartments/{id}`                 |
| Residents  | `POST/GET /residents` (`?apartment_id=` filter), `GET/PUT/DELETE /residents/{id}` |
| Saunas     | `POST/GET /saunas`, `GET/PUT/DELETE /saunas/{id}`                         |

Rules:

- Apartment numbers, resident emails and sauna names are unique.
- A resident must belong to an existing apartment.
- An apartment with residents cannot be deleted (`409`).
- Missing resources return `404`; invalid input returns `422`.

## Assumptions

- The system serves a single apartment building with one or more saunas.
- Sauna turns are one hour long and start on the full hour.
- All times are in the Europe/Helsinki time zone.

## Limitations

- Backend only; no frontend.
- No authentication or authorisation; admin endpoints are open in this course scope.
- Weekly turns and one-off bookings are not implemented yet.

## Team

- Fan Yin
