"""Request and response models for /weekly-turns."""

from datetime import time
from uuid import UUID

from pydantic import BaseModel, Field

from saunavuoro.domain.weekly_turn import WeeklyTurn


class WeeklyTurnIn(BaseModel):
    """Data for assigning or changing an apartment's weekly turn."""

    sauna_id: UUID = Field(description="The sauna of the turn.")
    apartment_id: UUID = Field(description="The apartment that has the turn.")
    weekday: int = Field(
        ge=0,
        le=6,
        description="Day of the week: 0 = Monday, 1 = Tuesday, …, 6 = Sunday.",
        examples=[4],
    )
    start_time: time = Field(
        description="Start time of the turn. Must be one of the sauna's turn start times.",
        examples=["18:00"],
    )


class WeeklyTurnOut(WeeklyTurnIn):
    """A fixed turn that an apartment has every week."""

    id: UUID = Field(description="Unique identifier of the weekly turn.")

    @classmethod
    def from_entity(cls, turn: WeeklyTurn) -> "WeeklyTurnOut":
        return cls(
            id=turn.id,
            sauna_id=turn.sauna_id,
            apartment_id=turn.apartment_id,
            weekday=turn.weekday,
            start_time=turn.start_time,
        )
