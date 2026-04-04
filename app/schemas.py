from enum import Enum
from random import randint
from pydantic import BaseModel, Field


def random_destination():
    return randint(11000, 11990)


class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


# class BaseShipment(BaseModel):
#     content: str = Field(max_length=30)
#     weight: float = Field(le=25, ge=1)
#     destination: int | None = Field(
#         # default=randint(11000, 11990)
#         default_factory=random_destination
#     )
#     status: ShipmentStatus


class BaseShipment(BaseModel):
    content: str = Field(max_length=30)
    weight: float = Field(le=25, ge=1)


class ShipmentRead(BaseShipment):
    status: ShipmentStatus


class ShipmentCreate(BaseShipment):
    pass


class ShipmentUpdate(BaseModel):
    status: ShipmentStatus
