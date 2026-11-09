"""Dependency Injection for the routers.

The composition root (main.py) decides which UnitOfWork is used;
the API layer only knows the UnitOfWork interface.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request

from saunavuoro.application.ports import UnitOfWork

UnitOfWorkFactory = Callable[[], UnitOfWork]


def get_uow(request: Request) -> UnitOfWork:
    factory: UnitOfWorkFactory = request.app.state.uow_factory
    return factory()


Uow = Annotated[UnitOfWork, Depends(get_uow)]
