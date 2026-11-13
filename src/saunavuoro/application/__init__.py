"""Public application API."""

from saunavuoro.application.apartments import (
    CreateApartment,
    DeleteApartment,
    GetApartment,
    ListApartments,
    UpdateApartment,
)
from saunavuoro.application.exceptions import (
    ApplicationError,
    ConflictError,
    EntityNotFoundError,
)
from saunavuoro.application.residents import (
    CreateResident,
    DeleteResident,
    GetResident,
    ListResidents,
    UpdateResident,
)
from saunavuoro.application.saunas import (
    CreateSauna,
    DeleteSauna,
    GetSauna,
    ListSaunas,
    UpdateSauna,
)

__all__ = [
    "ApplicationError",
    "ConflictError",
    "CreateApartment",
    "CreateResident",
    "CreateSauna",
    "DeleteApartment",
    "DeleteResident",
    "DeleteSauna",
    "EntityNotFoundError",
    "GetApartment",
    "GetResident",
    "GetSauna",
    "ListApartments",
    "ListResidents",
    "ListSaunas",
    "UpdateApartment",
    "UpdateResident",
    "UpdateSauna",
]
