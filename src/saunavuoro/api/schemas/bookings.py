from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from saunavuoro.domain.booking import Booking


class BookingIn(BaseModel):
    sauna_id: UUID = Field(description="Sauna to be booked.")
    apartment_id: UUID = Field(description="Apartment making the booking.")
    starts_at: datetime = Field(description="Booking start time.")
    ends_at: datetime = Field(description="Booking end time.")


class BookingOut(BaseModel):
    id: UUID = Field(description="Unique booking identifier.")
    sauna_id: UUID = Field(description="Booked sauna.")
    apartment_id: UUID = Field(description="Apartment making the booking.")
    starts_at: datetime
    ends_at: datetime

    @classmethod
    def from_entity(cls, booking: Booking) -> "BookingOut":
        return cls(
            id=booking.id,
            sauna_id=booking.sauna_id,
            apartment_id=booking.apartment_id,
            starts_at=booking.starts_at,
            ends_at=booking.ends_at,
        )