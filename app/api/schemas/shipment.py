from calendar import c
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.database.models import ShipmentEvent, ShipmentStatus


class BaseShipment(BaseModel):
    content: str
    weight: float = Field(le=25)
    destination: int


class ShipmentRead(BaseShipment):
    id: UUID
    timeline: list[ShipmentEvent]
    estimated_delivery: datetime


class ShipmentCreate(BaseShipment):
    client_contact_email: EmailStr
    client_contact_phone: str | None = Field(default=None)

class ShipmentUpdate(BaseModel):
    location: int | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    verification_code: str | None = Field(default=None, exclude=True)

class ShipmentReview(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None)
    