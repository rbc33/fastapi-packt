from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.database.models import ShipmentEvent, ShipmentStatus, TagName


class BaseShipment(BaseModel):
    content: str = Field(max_length=100)
    weight: float = Field(le=25)
    destination: int = Field(
        description="instead use location, location zipcode",
        examples=[1,2,3],
        deprecated=True,
    )
    location: int


class TagRead(BaseModel):
    name: TagName
    instruction: str

class ShipmentRead(BaseShipment):
    id: UUID
    timeline: list[ShipmentEvent]
    estimated_delivery: datetime
    tags: list[TagRead]


class ShipmentCreate(BaseShipment):
    """Shipment details to create a new shipment"""
    client_contact_email: EmailStr
    client_contact_phone: str | None = Field(default=None)

class ShipmentUpdate(BaseModel):
    location: int | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    verification_code: str | None = Field(default=None, exclude=True)

class ShipmentReview(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None)
    