"""FastAPI dependencies (the composition root for adapters)."""

from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from saunavuoro.infrastructure.config import get_settings
from saunavuoro.infrastructure.database import Database


@lru_cache
def get_database() -> Database:
    return Database(get_settings().database_url)


def get_session(
    database: Annotated[Database, Depends(get_database)],
) -> Iterator[Session]:
    with database.session() as session:
        yield session


DatabaseDep = Annotated[Database, Depends(get_database)]
SessionDep = Annotated[Session, Depends(get_session)]
