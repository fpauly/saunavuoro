# ADR 0006: Implement booking rules as separate rule components

- **Status:** Proposed
- **Date:** 2026-11-28

## Context

The value of SaunaVuoro is in its booking rules, and the topic proposal expects new rules to be added later (for example maintenance closures) without modifying existing use cases (Open/Closed Principle, extensibility requirement). A one-off booking must currently pass these rules:

1. The start time is a turn start inside the sauna's opening hours.
2. The turn is not in the past and not more than `max_days_ahead` days ahead.
3. The turn is not already booked and does not clash with a weekly turn.
4. The apartment has fewer than `max_extra_bookings_per_week` bookings in that week.

Cancelling has its own rule: the booking cannot be cancelled less than `cancellation_deadline_hours` before it starts.

If all checks are written directly in `CreateBooking.execute()`, the method grows with every new rule, and each rule can only be tested through the whole use case.

## Decision

Each rule is a small class that implements one interface:

```python
class BookingRule(Protocol):
    def check(self, request: BookingRequest, context: BookingContext) -> None:
        """Raise RuleViolationError if the rule is broken."""
```

- `BookingRequest` holds the sauna, the apartment and the start time.
- `BookingContext` holds the data the rules need, loaded once by the use case: the current time, existing bookings of the sauna and of the apartment for that week, and the weekly turns of the sauna.
- Rules that need only domain data live in the domain layer (`domain/booking_rules.py`) and do not use repositories.
- `CreateBooking` receives a list of rules in its constructor, loads the context, calls every rule, and saves the booking. The list is built in the composition root.

Adding a rule, such as a maintenance closure, means writing a new class and adding it to the list. `CreateBooking` does not change.

## Alternatives considered

| Option | Pros | Cons |
| ------ | ---- | ---- |
| **All checks inside the use case** | Easy to read at first; least code | The use case grows with every rule; violates Open/Closed; rules are hard to test alone |
| **Rules as methods of the `Sauna` entity** | Rules are in the domain, close to their data | `Sauna` would need all bookings and weekly turns; the entity becomes large |
| **Specification pattern with `and` / `or` combinators** | Very flexible | More abstraction than our rules need |
| **Rule components with a shared context** (chosen) | One class per rule; each rule unit tested alone; new rules without changing the use case; shows SRP and OCP | More classes; the order of rules decides which error is reported first; the context must contain everything any rule might need |

## Consequences

- **Positive:** Each rule has its own unit tests with `FixedClock` and plain domain objects, with no repositories.
- **Positive:** Error messages are specific, because each rule raises its own message (for example "Apartment A 12 already has 1 extra booking in week 49.").
- **Negative:** Only the first broken rule is reported. Collecting all broken rules would need a different return value and is not needed for the API.
- **Negative:** When a new rule needs new data, `BookingContext` and the use case that loads it must still change.
- **Status note:** The booking use cases on the `ronja` branch currently check only that the slot is free. This ADR describes the target design for the remaining rules and will be marked Accepted when they are implemented.
