"""Errors raised when a business rule is broken."""


class DomainError(Exception):
    """Base class for all domain errors."""


class InvalidApartmentNumberError(DomainError):
    """The apartment number is empty or too long."""


class RuleViolationError(DomainError):
    pass
