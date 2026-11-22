from datetime import date
from uuid import UUID

from fastapi import APIRouter, Query, status

from saunavuoro.api.dependencies import Uow
from saunavuoro.api.schemas.bookings import BookingIn, BookingOut
from saunavuoro.api.schemas.errors import error_responses
from saunavuoro.application.use_cases.bookings import (
    CheckAvailability,
    CreateBooking,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get(
    "/availability",
    summary="Check sauna availability",
    responses=error_responses(404, 422),
)
def check_availability(
    sauna_id: UUID,
    booking_date: date = Query(description="Date to check availability"),
    uow: Uow = None,
) -> list[str]:
    """Return all free turn start times for a sauna on a given day."""
    available_slots = CheckAvailability(uow).execute(
        sauna_id,
        booking_date,
    )

    return [slot.isoformat() for slot in available_slots]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a booking",
    responses=error_responses(404, 409, 422),
)
def create_booking(
    body: BookingIn,
    uow: Uow,
) -> BookingOut:
    """Create a one-off sauna booking."""

    booking = CreateBooking(uow).execute(
        body.sauna_id,
        body.apartment_id,
        body.starts_at,
        body.ends_at,
    )

    return BookingOut.from_entity(booking)