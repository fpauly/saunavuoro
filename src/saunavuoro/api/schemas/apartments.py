"""Request and response models for /apartments.

The API never returns domain entities directly; it converts them here.
"""

from uuid import UUID

from pydantic import BaseModel, Field

from saunavuoro.domain.apartment import Apartment


class ApartmentIn(BaseModel):
    """Data for creating or updating an apartment."""

    number: str = Field(
        min_length=1,
        max_length=20,
        description="Apartment number. Stored in upper case without extra spaces.",
        examples=["A 12"],
    )


class ApartmentOut(BaseModel):
    """An apartment in the building."""

    id: UUID = Field(description="Unique identifier of the apartment.")
    number: str = Field(description="Apartment number.", examples=["A 12"])

    @classmethod
    def from_entity(cls, apartment: Apartment) -> "ApartmentOut":
        return cls(id=apartment.id, number=apartment.number)
