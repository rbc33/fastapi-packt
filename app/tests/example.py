from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import DeliveryPartner, Seller, Shipment, ShipmentEvent, ShipmentStatus, Tag, TagName
from app.services.user import hash_password

TEST_SHIPMENT_ID = UUID("343a57d5-e1c0-4fdb-adfd-b4926f0e1b33")

SELLER = {
    "name": "RainForest",
    "email": "rainforest@xmailg.one",
    "password": "lovetrees",
    "zip_code": 11001,
}
DELIVERY_PARTNER = {
    "name": "PHL",
    "email": "phl@xmailg.one",
    "password": "tough",
    "max_handling_capacity": 2,
    "serviceable_zip_codes": [11001, 11002, 11003, 11004, 11005],
}
SHIPMENT = {
    "content": "Bananas",
    "weight": 1.25,
    "destination": 11004,
    "client_contact_email": "py@xmailg.one",
}


async def create_test_data(session: AsyncSession):
    seller = Seller(
        name=SELLER["name"],
        email=SELLER["email"],
        zip_code=SELLER["zip_code"],
        email_verified=True,
        password_hash=hash_password(SELLER["password"]),
        created_at=datetime.now(),
    )
    partner = DeliveryPartner(
        name=DELIVERY_PARTNER["name"],
        email=DELIVERY_PARTNER["email"],
        email_verified=True,
        password_hash=hash_password(DELIVERY_PARTNER["password"]),
        serviceable_zip_codes=DELIVERY_PARTNER["serviceable_zip_codes"],
        max_handling_capacity=DELIVERY_PARTNER["max_handling_capacity"],
        created_at=datetime.now(),
    )
    session.add(seller)
    session.add(partner)
    await session.commit()
    await session.refresh(seller)
    await session.refresh(partner)

    shipment = Shipment(
        id=TEST_SHIPMENT_ID,
        content=SHIPMENT["content"],
        weight=SHIPMENT["weight"],
        destination=SHIPMENT["destination"],
        client_contact_email=SHIPMENT["client_contact_email"],
        client_contact_phone=None,
        estimated_delivery=datetime.now() + timedelta(days=3),
        seller_id=seller.id,
        delivery_partner_id=partner.id,
        created_at=datetime.now(),
    )
    session.add(shipment)
    await session.commit()

    event = ShipmentEvent(
        location=SHIPMENT["destination"],
        status=ShipmentStatus.placed,
        shipment_id=TEST_SHIPMENT_ID,
        created_at=datetime.now(),
    )
    session.add(event)

    for name, instruction in [
        (TagName.EXPRESS, "Deliver as fast as possible"),
        (TagName.FRAGILE, "Handle with care"),
        (TagName.HEAVY, "Use proper lifting equipment"),
    ]:
        session.add(Tag(name=name, instruction=instruction))

    await session.commit()
