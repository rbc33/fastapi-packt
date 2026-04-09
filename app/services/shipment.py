from datetime import datetime, timedelta
from uuid import UUID

from fastapi import HTTPException, status

from app.api.schemas.shipment import ShipmentCreate
from app.database.models import Seller, Shipment, ShipmentStatus
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base import BaseService


class ShipmentService(BaseService):
    def __init__(self, session: AsyncSession):
        super().__init__(Shipment, session)

    async def get(self, id: UUID) -> Shipment | None:
        return await self._get(id)

    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now() + timedelta(days=3),
            seller_id=seller.id
        )
        return await self._add(new_shipment)
     

    async def update(self, id: UUID, shipment_update: dict) -> Shipment:
        shipment = await self.get(id)
        if shipment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        shipment.sqlmodel_update(shipment_update)
        return await self._update(shipment)

    async def delete(self, id: UUID):
        shipment = await self.get(id)
        if shipment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        await self._delete(shipment)
