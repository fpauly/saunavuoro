from datetime import date, datetime, time, timedelta
from uuid import UUID

from saunavuoro.application.errors import ConflictError, NotFoundError
from saunavuoro.application.ports import UnitOfWork
from saunavuoro.domain.booking import Booking


class CheckAvailability:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(
        self,
        sauna_id: UUID,
        booking_date: date,
    ) -> list[time]:
        with self._uow as uow:
            sauna = uow.saunas.get(sauna_id)

            if sauna is None:
                raise NotFoundError(
                    "Sauna",
                    sauna_id,
                )

            start_of_day = datetime.combine(
                booking_date,
                time.min,
            )

            end_of_day = start_of_day + timedelta(days=1)

            bookings = uow.bookings.list_by_sauna(
                sauna_id,
                start_of_day,
                end_of_day,
            )

            booked_times = {
                booking.starts_at.time()
                for booking in bookings
            }

            return [
                slot
                for slot in sauna.turn_start_times()
                if slot not in booked_times
            ]
    
class CreateBooking:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(
        self,
        sauna_id: UUID,
        apartment_id: UUID,
        starts_at: datetime,
        ends_at: datetime,
    ) -> Booking:
        booking = Booking(
            sauna_id=sauna_id,
            apartment_id=apartment_id,
            starts_at=starts_at,
            ends_at=ends_at,
        )

        with self._uow as uow:
            if uow.saunas.get(sauna_id) is None:
                raise NotFoundError("Sauna", sauna_id)

            if uow.apartments.get(apartment_id) is None:
                raise NotFoundError("Apartment", apartment_id)

            existing_booking = uow.bookings.get_by_slot(
                sauna_id,
                starts_at,
            )

            if existing_booking is not None:
                raise ConflictError(
                    "This sauna turn is already booked."
                )

            uow.bookings.add(booking)
            uow.commit()

        return booking


class CancelBooking:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(
        self,
        booking_id: UUID,
    ) -> None:
        with self._uow as uow:
            booking = uow.bookings.get(booking_id)

            if booking is None:
                raise NotFoundError(
                    "Booking",
                    booking_id,
                )

            uow.bookings.delete(
                booking_id,
            )

            uow.commit()


class ListApartmentBookings:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def execute(
        self,
        apartment_id: UUID,
    ) -> tuple[list[Booking], UUID | None]:
        with self._uow as uow:
            if uow.apartments.get(apartment_id) is None:
                raise NotFoundError(
                    "Apartment",
                    apartment_id,
                )

            weekly_turn = uow.weekly_turns.get_by_apartment(
                apartment_id,
            )

            bookings = uow.bookings.list_by_apartment(
                apartment_id,
                datetime.now(),
                datetime.max,
            )

            weekly_turn_id = None

            if weekly_turn is not None:
                weekly_turn_id = weekly_turn.id

            return bookings, weekly_turn_id
        