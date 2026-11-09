"""Errors raised by use cases."""

from uuid import UUID


class ApplicationError(Exception):
    """Base class for application errors."""


class NotFoundError(ApplicationError):
    def __init__(self, resource: str, resource_id: UUID) -> None:
        super().__init__(f"{resource} {resource_id} was not found.")


class AlreadyExistsError(ApplicationError):
    """A resource with the same unique value already exists."""
