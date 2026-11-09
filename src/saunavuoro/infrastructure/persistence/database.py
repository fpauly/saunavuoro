from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for all ORM models."""


def make_session_factory(database_url: str) -> sessionmaker[Session]:
    return sessionmaker(bind=create_engine(database_url), expire_on_commit=False)
