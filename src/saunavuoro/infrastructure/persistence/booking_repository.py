from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from saunavuoro.domain.booking import Booking
from saunavuoro.infrastructure.persistence.models import BookingModel


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def _db(value: datetime) -> datetime:
    return value.astimezone(UTC)


def _to_entity(row: BookingModel) -> Booking:
    return Booking(
        id=row.id,
        sauna_id=row.sauna_id,
        apartment_id=row.apartment_id,
        starts_at=_aware(row.starts_at),
        ends_at=_aware(row.ends_at),
    )


class SqlAlchemyBookingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, booking: Booking) -> None:
        self._session.add(
            BookingModel(
                id=booking.id,
                sauna_id=booking.sauna_id,
                apartment_id=booking.apartment_id,
                starts_at=_db(booking.starts_at),
                ends_at=_db(booking.ends_at),
            )
        )

    def get(self, booking_id: UUID) -> Booking | None:
        row = self._session.get(BookingModel, booking_id)
        return _to_entity(row) if row else None

    def get_by_slot(self, sauna_id: UUID, starts_at: datetime) -> Booking | None:
        row = self._session.scalar(
            select(BookingModel).where(
                BookingModel.sauna_id == sauna_id, BookingModel.starts_at == _db(starts_at)
            )
        )
        return _to_entity(row) if row else None

    def list_by_sauna(self, sauna_id: UUID, start: datetime, end: datetime) -> list[Booking]:
        rows = self._session.scalars(
            select(BookingModel)
            .where(
                BookingModel.sauna_id == sauna_id,
                BookingModel.starts_at >= _db(start),
                BookingModel.starts_at < _db(end),
            )
            .order_by(BookingModel.starts_at)
        )
        return [_to_entity(row) for row in rows]

    def list_by_apartment(
        self, apartment_id: UUID, start: datetime, end: datetime
    ) -> list[Booking]:
        rows = self._session.scalars(
            select(BookingModel)
            .where(
                BookingModel.apartment_id == apartment_id,
                BookingModel.starts_at >= _db(start),
                BookingModel.starts_at < _db(end),
            )
            .order_by(BookingModel.starts_at)
        )
        return [_to_entity(row) for row in rows]

    def delete(self, booking_id: UUID) -> None:
        row = self._session.get(BookingModel, booking_id)
        if row is not None:
            self._session.delete(row)
