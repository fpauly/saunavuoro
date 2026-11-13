"""Application-level exceptions.

Use cases raise these when an operation cannot be completed because of the
current application state (as opposed to invalid input).
"""


class ApplicationError(Exception):
    """Base class for application errors."""


class EntityNotFoundError(ApplicationError):
    """Raised when the requested entity does not exist."""

    def __init__(self, entity: str, entity_id: int) -> None:
        super().__init__(f"{entity} with id {entity_id} was not found.")
        self.entity = entity
        self.entity_id = entity_id


class ConflictError(ApplicationError):
    """Raised when an operation conflicts with existing data or rules."""
