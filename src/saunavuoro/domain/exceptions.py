"""Domain-level exceptions.

These errors describe broken business rules and are independent of any
framework or transport. The API layer translates them into HTTP responses.
"""


class DomainError(Exception):
    """Base class for all domain errors."""


class DomainValidationError(DomainError):
    """Raised when an entity would be created in an invalid state."""
