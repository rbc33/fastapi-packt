from datetime import datetime
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, UniqueConstraint


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class Shipment(SQLModel, table=True):
    __tablename__ = "shipment"

    id: int = Field(default=None,primary_key=True) # type: ignore
    content: str
    weight: float = Field(le=25)
    destination: int
    status: ShipmentStatus
    estimated_delivery: datetime

class Seller(SQLModel, table = True):
    __table_args__ = (UniqueConstraint("email"),)

    id: int = Field(default=None,primary_key=True) # type: ignore
    name: str
    email: EmailStr
    password_hash: str
