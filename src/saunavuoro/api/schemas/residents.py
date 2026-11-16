"""Request and response models for /residents."""

from uuid import UUID

from pydantic import BaseModel, Field

from saunavuoro.domain.resident import Resident


class ResidentIn(BaseModel):
    """Data for creating or updating a resident."""

    apartment_id: UUID = Field(description="Apartment the resident lives in.")
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Full name of the resident.",
        examples=["Maija Virtanen"],
    )


class ResidentOut(BaseModel):
    """A resident of the building."""

    id: UUID = Field(description="Unique identifier of the resident.")
    apartment_id: UUID = Field(description="Apartment the resident lives in.")
    name: str = Field(description="Full name of the resident.", examples=["Maija Virtanen"])

    @classmethod
    def from_entity(cls, resident: Resident) -> "ResidentOut":
        return cls(id=resident.id, apartment_id=resident.apartment_id, name=resident.name)
