# ADR 0005: Handle time with an injected clock, local time in the domain and UTC in the database

- **Status:** Accepted
- **Date:** 2026-11-28

## Context

Many booking rules depend on the current time: a turn cannot be booked in the past or more than `max_days_ahead` days ahead, and it cannot be cancelled less than `cancellation_deadline_hours` before it starts. Opening hours and weekly turns are local wall-clock times ("Tuesdays at 18:00"). Finland changes between summer and winter time, so the same local time has a different UTC offset during the year.

Tests must be able to check these rules at a fixed moment, without depending on when the tests are run.

## Decision

- The current time comes from a **`Clock` port** (`application/ports.py`) with one method, `now()`. Use cases get the clock as a constructor argument, and routers get it with the `CurrentClock` dependency.
- `SystemClock` returns an aware datetime in **Europe/Helsinki**. `FixedClock` returns a given moment and is used in tests. The composition root (`main.py`) chooses `SystemClock`.
- Opening hours and weekly turns are stored as local `time` values (no date, no time zone). One-off bookings are aware datetimes and are stored as **UTC** in `timestamptz` columns; the repository converts them (`_db()`, `_aware()` in `booking_repository.py`).
- The system serves one building, so Europe/Helsinki is the only time zone (see Assumptions in the README).

## Alternatives considered

| Option | Pros | Cons |
| ------ | ---- | ---- |
| **Call `datetime.now()` directly in the code** | Least code | Rules cannot be tested at a fixed moment; tests become flaky around deadlines |
| **Store local time without time zone** | Matches how residents think about turns | Ambiguous during the daylight saving change in autumn; comparing with "now" is error-prone |
| **Use UTC everywhere, also for opening hours** | One time zone in the code | "Opens at 16:00" would move by one hour twice a year |
| **Injected clock, local rules, UTC storage** (chosen) | Deterministic tests; correct around daylight saving changes; standard practice for stored timestamps | Conversions between local time and UTC in the repository and when building turn times |

## Consequences

- **Positive:** Time-based rules can be unit tested with `FixedClock`, for example one minute before and after the cancellation deadline. The booking tests must use it.
- **Positive:** The `Clock` port is a clear example of the Dependency Inversion Principle: the use cases depend on an abstraction, not on the system clock.
- **Negative:** All datetimes must be timezone-aware. A naive datetime would be compared wrongly; SQLite returns naive values, so the repository has to add UTC back (`_aware()`).
- **Negative:** On the night when clocks go back, the hour 03:00–04:00 exists twice. Because saunas are not open at night, we do not handle this case.
