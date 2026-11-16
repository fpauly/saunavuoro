"""Request and response models for /saunas."""

from datetime import time
from uuid import UUID

from pydantic import BaseModel, Field

from saunavuoro.domain.sauna import Sauna


class SaunaIn(BaseModel):
    """Data for creating or updating a sauna."""

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Name of the sauna.",
        examples=["Lower sauna"],
    )
    opens_at: time = Field(description="Opening time of the sauna.", examples=["17:00"])
    closes_at: time = Field(description="Closing time of the sauna.", examples=["22:00"])
    turn_length_minutes: int = Field(
        default=60,
        ge=1,
        description="Length of one sauna turn in minutes.",
        examples=[60],
    )
    max_extra_bookings_per_week: int = Field(
        default=1,
        ge=0,
        description="How many extra one-off bookings an apartment may make per week.",
        examples=[1],
    )
    max_days_ahead: int = Field(
        default=14,
        ge=0,
        description="How many days ahead bookings can be made.",
        examples=[14],
    )
    cancellation_deadline_hours: int = Field(
        default=2,
        ge=0,
        description="How many hours before a turn a booking can be cancelled.",
        examples=[2],
    )


class SaunaOut(SaunaIn):
    """A sauna of the building."""

    id: UUID = Field(description="Unique identifier of the sauna.")

    @classmethod
    def from_entity(cls, sauna: Sauna) -> "SaunaOut":
        return cls(
            id=sauna.id,
            name=sauna.name,
            opens_at=sauna.opens_at,
            closes_at=sauna.closes_at,
            turn_length_minutes=sauna.turn_length_minutes,
            max_extra_bookings_per_week=sauna.max_extra_bookings_per_week,
            max_days_ahead=sauna.max_days_ahead,
            cancellation_deadline_hours=sauna.cancellation_deadline_hours,
        )
