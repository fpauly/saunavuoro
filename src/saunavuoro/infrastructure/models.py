"""SQLAlchemy ORM models.

These models are persistence concerns only. Business rules live in the
domain entities, and repositories translate between the two.
"""

from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from saunavuoro.infrastructure.database import Base


class ApartmentModel(Base):
    __tablename__ = "apartments"
    __table_args__ = (
        CheckConstraint("floor >= 1", name="floor_positive"),
        UniqueConstraint("number", name="uq_apartments_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(20), nullable=False)
    floor: Mapped[int] = mapped_column(nullable=False)

    residents: Mapped[list[ResidentModel]] = relationship(
        back_populates="apartment",
        passive_deletes=True,
    )


class ResidentModel(Base):
    __tablename__ = "residents"
    __table_args__ = (
        CheckConstraint("apartment_id > 0", name="apartment_id_positive"),
        UniqueConstraint("email", name="uq_residents_email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    apartment_id: Mapped[int] = mapped_column(
        ForeignKey("apartments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    apartment: Mapped[ApartmentModel] = relationship(back_populates="residents")


class SaunaModel(Base):
    __tablename__ = "saunas"
    __table_args__ = (
        CheckConstraint("capacity >= 1 AND capacity <= 1000", name="capacity_range"),
        UniqueConstraint("name", name="uq_saunas_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    capacity: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
