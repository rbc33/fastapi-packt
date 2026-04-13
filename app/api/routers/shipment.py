import re
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import DeliveryPartnerDep, SellerDep, ShipmentServiceDep
from app.database.models import Shipment
from app.api.schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate
from app.utils import TEMPLATE_DIR

router = APIRouter(prefix="/shipment", tags=["Shipment"])

templates = Jinja2Templates(TEMPLATE_DIR)


@router.get("/", response_model=Shipment)
async def get_shipment(
    id: UUID,
    _: SellerDep,
    service: ShipmentServiceDep,
):
    shipment = await service.get(id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesnt exist!"
        )
    return shipment


### Tracking details of shipment
@router.get("/track")
async def get_track(
    request: Request,
    id: UUID,
    service: ShipmentServiceDep,
):
    shipment = await service.get(id)
    context = shipment.model_dump()
    context["partner"] = shipment.delivery_partner.name
    context["status"] = shipment.status
    context["timeline"] = shipment.timeline
    return templates.TemplateResponse(
        request=request,
        name="track.html",
        context=context,
    )


@router.post("/")
async def submit_shipment(
    seller: SellerDep,
    shipment: ShipmentCreate,
    service: ShipmentServiceDep,
) -> Shipment:
    return await service.add(shipment, seller)


@router.get("/{field}")
async def get_shipment_field(
    field: str,
    id: UUID,
    _: SellerDep,
    service: ShipmentServiceDep,
) -> Any:
    shipment = await service.get(id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesnt exist!"
        )
    if not hasattr(shipment, field):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Field doesn't exist"
        )
    return getattr(shipment, field)


# @router.put("/")
# async def shipment_update(id: int, data: dict[str, Any])-> dict[str,Any]:
#     content = data.get("content")
#     weight = data.get("weight")
#     status = data.get("status")
#     shipments[id] = {
#         "content": content,
#         "weight": weight,
#         "status": status
#     }
#     return shipments[id]


@router.patch("/", response_model=ShipmentRead)
async def update_shipment(
    id: UUID,
    shipment_update: ShipmentUpdate,
    partner: DeliveryPartnerDep,
    service: ShipmentServiceDep,
):
    # Update data with given fields
    update = shipment_update.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided to update",
        )

    return await service.update(id, shipment_update, partner)


        
        
@router.get("/cancel", response_model=ShipmentRead)
async def cancel_shipment(
    id: UUID,
    seller: SellerDep,
    service: ShipmentServiceDep,
):
    return await service.cancel(id, seller)

