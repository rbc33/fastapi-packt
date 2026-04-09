from pydantic import BaseModel, EmailStr


class BaseDeliveryPartner(BaseModel):
    name: str
    email: EmailStr
    serviceable_zip_codes: list[int]
    max_hanling_capacity: int


class DeliveryPartnerRead(BaseDeliveryPartner):
    pass

class DeliveryPartnerUpdate(BaseDeliveryPartner):
    serviceable_zip_codes: list[int]
    max_hanling_capacity: int


class DeliveryPartnerCreate(BaseDeliveryPartner):
    password: str
