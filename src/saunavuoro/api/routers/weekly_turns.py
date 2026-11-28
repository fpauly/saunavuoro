"""/weekly-turns endpoints. Routers only convert data and call use cases (no business logic).

The docstring of each endpoint is shown as its description in Swagger UI.
"""

from uuid import UUID

from fastapi import APIRouter, status

from saunavuoro.api.dependencies import Uow
from saunavuoro.api.schemas.errors import error_responses
from saunavuoro.api.schemas.weekly_turns import WeeklyTurnIn, WeeklyTurnOut
from saunavuoro.application.use_cases.weekly_turns import (
    AssignWeeklyTurn,
    ChangeWeeklyTurn,
    GetWeeklyTurn,
    ListWeeklyTurns,
    RemoveWeeklyTurn,
)

router = APIRouter(prefix="/weekly-turns", tags=["weekly-turns"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Assign a weekly turn",
    responses=error_responses(404, 409, 422),
)
def assign_weekly_turn(body: WeeklyTurnIn, uow: Uow) -> WeeklyTurnOut:
    """Give an apartment a fixed turn in a sauna every week.

    An apartment can have only one weekly turn, and a turn can belong to only one apartment.
    The start time must be one of the sauna's turn start times.
    """
    turn = AssignWeeklyTurn(uow).execute(
        body.sauna_id, body.apartment_id, body.weekday, body.start_time
    )
    return WeeklyTurnOut.from_entity(turn)


@router.get("", summary="List weekly turns", responses=error_responses(422))
def list_weekly_turns(
    uow: Uow, sauna_id: UUID | None = None, apartment_id: UUID | None = None
) -> list[WeeklyTurnOut]:
    """Return weekly turns sorted by weekday and start time.

    Use `sauna_id` to see all turns of one sauna, or `apartment_id` to see an apartment's turn.
    """
    turns = ListWeeklyTurns(uow).execute(sauna_id=sauna_id, apartment_id=apartment_id)
    return [WeeklyTurnOut.from_entity(t) for t in turns]


@router.get(
    "/{turn_id}",
    summary="Get a weekly turn",
    responses=error_responses(404, 422),
)
def get_weekly_turn(turn_id: UUID, uow: Uow) -> WeeklyTurnOut:
    """Return one weekly turn by id."""
    return WeeklyTurnOut.from_entity(GetWeeklyTurn(uow).execute(turn_id))


@router.put(
    "/{turn_id}",
    summary="Change a weekly turn",
    responses=error_responses(404, 409, 422),
)
def change_weekly_turn(turn_id: UUID, body: WeeklyTurnIn, uow: Uow) -> WeeklyTurnOut:
    """Move a weekly turn to another day, time or sauna, or give it to another apartment."""
    turn = ChangeWeeklyTurn(uow).execute(
        turn_id, body.sauna_id, body.apartment_id, body.weekday, body.start_time
    )
    return WeeklyTurnOut.from_entity(turn)


@router.delete(
    "/{turn_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a weekly turn",
    responses=error_responses(404, 422),
)
def remove_weekly_turn(turn_id: UUID, uow: Uow) -> None:
    """Remove an apartment's weekly turn. The time becomes free for one-off bookings."""
    RemoveWeeklyTurn(uow).execute(turn_id)
