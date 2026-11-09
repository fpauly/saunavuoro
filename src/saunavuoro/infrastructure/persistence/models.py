"""SQLAlchemy table definitions. Only the infrastructure layer knows about them."""

from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from saunavuoro.infrastructure.persistence.database import Base


class ApartmentModel(Base):
    __tablename__ = "apartments"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(20), unique=True)
