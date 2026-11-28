# ADR 0002: Prevent double bookings with database constraints and a unit of work

- **Status:** Accepted
- **Date:** 2026-11-28

## Context

Data integrity is one of our three most important quality attributes (see the topic proposal): a sauna turn must never be booked twice, even when two residents try to book the same turn at the same moment. The use cases check availability before saving (`get_by_slot()`), but a check in application code alone is not safe. Two requests can both see the turn as free and both save it.

Turns are on a fixed time grid: a turn starts at `opens_at + n × turn_length_minutes` (`Sauna.turn_start_times()`). Two bookings of the same sauna therefore overlap only if they have the same start time.

## Decision

We protect integrity on two levels:

1. **Domain and application checks** give a clear error message in the normal case. The domain checks that a start time is on the grid and inside the opening hours; the use case checks that the slot is free.
2. **Database constraints** guarantee integrity when requests run at the same time:
   - `uq_bookings_slot`: `UNIQUE (sauna_id, starts_at)` on `bookings`
   - `uq_weekly_turns_slot`: `UNIQUE (sauna_id, weekday, start_time)` on `weekly_turns`
   - `UNIQUE (apartment_id)` on `weekly_turns`: at most one weekly turn per apartment
   - `CHECK` constraints on `saunas` and `bookings` (for example `closes_at > opens_at`, `ends_at > starts_at`)
   - `ON DELETE RESTRICT` foreign keys from bookings and weekly turns, so a sauna or apartment that still has turns cannot be deleted by accident

Every use case runs inside a **unit of work** (`UnitOfWork` port, `SqlAlchemyUnitOfWork` implementation). One use case is one transaction: changes are saved only when `commit()` is called and are rolled back otherwise. If `commit()` fails with an `IntegrityError`, the unit of work raises the application's `ConflictError`, which the API returns as `409 Conflict`. The use cases never see SQLAlchemy errors.

## Alternatives considered

| Option | Pros | Cons |
| ------ | ---- | ---- |
| **Application checks only** | Simple; all rules in one place | Race condition: two parallel requests can both pass the check |
| **Pessimistic locking** (`SELECT … FOR UPDATE` on the sauna row) | Also protects rules a constraint cannot express, such as the weekly limit | Locking code in the repositories; requests for the same sauna are serialised; easy to get wrong |
| **PostgreSQL exclusion constraint** (`EXCLUDE USING gist (sauna_id WITH =, tstzrange(starts_at, ends_at) WITH &&)`) | Prevents any overlap, even if the turn length changes | Needs the `btree_gist` extension; cannot run on SQLite in tests; more than we need while turns are on a fixed grid |
| **Unique constraints + unit of work** (chosen) | The database guarantees no double booking; works on PostgreSQL and SQLite; the application layer stays free of database code | Only identical start times are caught; some rules are still checked only in code (see below) |

## Consequences

- **Positive:** A double booking is impossible at database level, whatever the application code does. `tests/integration/test_repositories.py` checks that a duplicate booking raises `ConflictError` with both the SQL and the in-memory unit of work.
- **Positive:** Use cases get transactions through a port, so they can be tested with `InMemoryUnitOfWork`.
- **Negative:** The constraint relies on the fixed time grid. If an administrator changes `turn_length_minutes` or `opens_at` while future bookings exist, old and new bookings could overlap without sharing a start time. Updating a sauna must therefore be rejected while it has future bookings, or we have to move to an exclusion constraint.
- **Negative:** Some rules are checked only in the use case: a one-off booking must not clash with a weekly turn (they are in different tables), and an apartment may have at most `max_extra_bookings_per_week` bookings. Two parallel requests from the same apartment could in theory exceed the weekly limit. We accept this because it needs two simultaneous requests from one household, and the result is one extra booking, not a double booking.
- **Negative:** A `409` caused by a constraint has a generic message ("The change conflicts with existing data."), because the unit of work does not inspect which constraint failed. The normal case still gets a specific message from the use case check.
