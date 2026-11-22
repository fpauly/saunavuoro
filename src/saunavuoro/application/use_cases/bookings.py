"""Booking use cases."""

from saunavuoro.application.ports import UnitOfWork


class CheckAvailability:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow