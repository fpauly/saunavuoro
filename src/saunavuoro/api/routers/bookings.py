from datetime import date
from uuid import UUID

from fastapi import APIRouter, Query

from saunavuoro.api.dependencies import Uow
from saunavuoro.api.schemas.errors import error_responses
from saunavuoro.application.use_cases.bookings import CheckAvailability

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