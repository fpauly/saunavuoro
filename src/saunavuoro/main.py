"""Composition root: the only place where concrete implementations are chosen.

Run with: uvicorn saunavuoro.main:app --reload
"""

from saunavuoro.api.app import create_app
from saunavuoro.infrastructure.config import load_settings
from saunavuoro.infrastructure.persistence.database import make_session_factory
from saunavuoro.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork

settings = load_settings()
session_factory = make_session_factory(settings.database_url)

app = create_app(uow_factory=lambda: SqlAlchemyUnitOfWork(session_factory))
