from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from app.services.base import BaseService
from app.services.notification import NotificationService


class ShipmentEventService(BaseService):
    def __init__(self, session, tasks):
        super().__init__(ShipmentEvent, session)
        self.notification_service = NotificationService(tasks)
        
        

    async def add(
        self,
        shipment,
        location: int =  None,
        status: ShipmentStatus = None,
        description: str = None,
    )-> ShipmentEvent:
        if location is None or status is None:
            last_event = await self.get_latest_event(shipment)
            if last_event is not None:
                if location is None:
                    location = last_event.location
                if status is None:
                    status = last_event.status
        new_event = ShipmentEvent(
            shipment_id=shipment.id,
            location=location,
            status=status,
            desription=description if description else self._generate_description(status, location),
        )
        await self._notify(shipment, status)
        return await self._add(new_event)
    
    async def get_latest_event(self, shipment: Shipment) -> ShipmentEvent | None:
        timeline = shipment.timeline
        if not timeline:
            return None
        timeline.sort(key=lambda e: e.created_at)
        return timeline[-1]
    
    def _generate_description(self, status: ShipmentStatus, location: int):
        match status:
            case ShipmentStatus.placed:
                return "assigned delivery partner"
            case ShipmentStatus.out_for_delivery:
                return "shipment out for delivery"
            case ShipmentStatus.delivered:
                return "successfully delivered"
            # case ShipmentStatus.cancelled:
            #     return "cancelled by seller"
            case _:  # and ShipmentStatus.in_transit
                return f"scanned at {location}"

    async def _notify(self, shipment: Shipment, status: ShipmentStatus):
        match status:
            case ShipmentStatus.placed:
                subject = "Shipment placed"
                body = f"Your shipment with id {shipment.id} has been placed and assigned to {shipment.delivery_partner.name}"
            case ShipmentStatus.in_transit:
                subject = "Shipment in transit"
                body = f"Your shipment with id {shipment.id} is in transit"
            case ShipmentStatus.out_for_delivery:
                subject = "Shipment out for delivery"
                body = f"Your shipment with id {shipment.id} is out for delivery"
            case ShipmentStatus.delivered:
                subject = "Shipment delivered"
                body = f"Your shipment with id {shipment.id} has been successfully delivered"
            case ShipmentStatus.cancelled:
                subject = "Shipment cancelled"
                body = f"Your shipment with id {shipment.id} has been cancelled by the seller"
            case _:
                return
        await self.notification_service.send_email(
            subject=subject,
            body=body,
            recipients=[shipment.client_contact_email],
        )