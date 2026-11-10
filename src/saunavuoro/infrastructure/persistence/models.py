"""SQLAlchemy table definitions. Only the infrastructure layer knows about them."""

from datetime import datetime, time
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from saunavuoro.infrastructure.persistence.database import Base


class ApartmentModel(Base):
    __tablename__ = "apartments"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(20), unique=True)


class ResidentModel(Base):
    __tablename__ = "residents"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    apartment_id: Mapped[UUID] = mapped_column(
        ForeignKey("apartments.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(100))


class SaunaModel(Base):
    __tablename__ = "saunas"
    __table_args__ = (CheckConstraint("closes_at > opens_at", name="ck_saunas_opening_hours"),)

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    opens_at: Mapped[time] = mapped_column(Time)
    closes_at: Mapped[time] = mapped_column(Time)
    turn_length_minutes: Mapped[int] = mapped_column(Integer)
    max_extra_bookings_per_week: Mapped[int] = mapped_column(Integer)
    max_days_ahead: Mapped[int] = mapped_column(Integer)
    cancellation_deadline_hours: Mapped[int] = mapped_column(Integer)


class WeeklyTurnModel(Base):
    __tablename__ = "weekly_turns"
    __table_args__ = (
        UniqueConstraint("sauna_id", "weekday", "start_time", name="uq_weekly_turns_slot"),
        CheckConstraint("weekday BETWEEN 0 AND 6", name="ck_weekly_turns_weekday"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    sauna_id: Mapped[UUID] = mapped_column(ForeignKey("saunas.id", ondelete="RESTRICT"))
    apartment_id: Mapped[UUID] = mapped_column(
        ForeignKey("apartments.id", ondelete="RESTRICT"), unique=True
    )
    weekday: Mapped[int] = mapped_column(SmallInteger)
    start_time: Mapped[time] = mapped_column(Time)


class BookingModel(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        UniqueConstraint("sauna_id", "starts_at", name="uq_bookings_slot"),
        CheckConstraint("ends_at > starts_at", name="ck_bookings_time_range"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True)
    sauna_id: Mapped[UUID] = mapped_column(ForeignKey("saunas.id", ondelete="RESTRICT"))
    apartment_id: Mapped[UUID] = mapped_column(
        ForeignKey("apartments.id", ondelete="RESTRICT"), index=True
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
