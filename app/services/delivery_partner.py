from typing import Sequence

from sqlmodel import select

from app.api.schemas.delivery_partner import DeliveryPartnerCreate
from app.core.exceptions import DeliveryPartnerNotAvailable
from app.database.models import DeliveryPartner, Shipment

from .user import UserService


class DeliveryPartnerService(UserService):
    def __init__(self, session):
        super().__init__(DeliveryPartner, session)

    async def add(self, delivery_partner: DeliveryPartnerCreate):
        return await self._add_user(delivery_partner.model_dump(), "partner")

    async def get_partner_by_zipcode(self, zipcode: int) -> Sequence[DeliveryPartner]:
        partners = (await self.session.scalars(select(DeliveryPartner))).all()
        return [p for p in partners if p.serviceable_zip_codes and zipcode in p.serviceable_zip_codes]
    
    async def assign_shipment(self, shipment: Shipment):
        eligible_partners = await self.get_partner_by_zipcode(shipment.destination)
        
        for partner in eligible_partners:
            if partner.current_handling_capacity > 0:
                partner.shipments.append(shipment)
                return partner

        # If no eliglible partners found or
        # parters have reached max handling capacity
        raise DeliveryPartnerNotAvailable()

    async def update(self, partner: DeliveryPartner):
        return await self._update(partner)

    async def token(self, email, password) -> str:
        return await self._generate_token(email, password)
