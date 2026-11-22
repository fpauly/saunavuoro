from datetime import date, datetime, time, timedelta
from uuid import UUID

from saunavuoro.application.errors import NotFoundError
from saunavuoro.application.ports import UnitOfWork


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
                raise NotFoundError("Sauna", sauna_id)

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