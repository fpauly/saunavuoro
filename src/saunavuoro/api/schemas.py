"""Request and response models for the REST API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ApartmentPayload(BaseModel):
    number: str = Field(min_length=1, max_length=20, examples=["A12"])
    floor: int = Field(ge=1, examples=[3])


class ApartmentCreate(ApartmentPayload):
    pass


class ApartmentUpdate(ApartmentPayload):
    pass


class ApartmentResponse(ApartmentPayload):
    model_config = ConfigDict(from_attributes=True)

    id: int


class ResidentPayload(BaseModel):
    first_name: str = Field(min_length=1, max_length=100, examples=["Maija"])
    last_name: str = Field(min_length=1, max_length=100, examples=["Virtanen"])
    email: EmailStr = Field(examples=["maija.virtanen@example.com"])
    phone: str | None = Field(default=None, max_length=30, examples=["+358 40 123 4567"])
    apartment_id: int = Field(ge=1, examples=[1])


class ResidentCreate(ResidentPayload):
    pass


class ResidentUpdate(ResidentPayload):
    pass


class ResidentResponse(ResidentPayload):
    model_config = ConfigDict(from_attributes=True)

    id: int


class SaunaPayload(BaseModel):
    name: str = Field(min_length=1, max_length=100, examples=["Main sauna"])
    location: str = Field(min_length=1, max_length=200, examples=["Ground floor"])
    capacity: int = Field(ge=1, le=1000, examples=[8])
    description: str | None = Field(
        default=None,
        max_length=500,
        examples=["Shared sauna with a dressing room."],
    )


class SaunaCreate(SaunaPayload):
    pass


class SaunaUpdate(SaunaPayload):
    pass


class SaunaResponse(SaunaPayload):
    model_config = ConfigDict(from_attributes=True)

    id: int
