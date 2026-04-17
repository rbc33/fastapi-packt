from enum import Enum


class APITag(str, Enum):
    SHIPMENT = "shipment"
    SELLER = "Seller"
    PARTNER = "delivery partner" 