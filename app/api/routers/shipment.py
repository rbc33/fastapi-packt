from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import ShipmentServiceDep
from app.database.models import Shipment
from app.api.schemas.shipment import ShipmentCreate, ShipmentRead, ShipmentUpdate

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.get("/", response_model=Shipment)
async def get_shipment(
    id: int,
    service: ShipmentServiceDep,
):
    shipment = await service.get(id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Given id doesnt exist!"
        )
    return shipment


@router.post("/")
async def submit_shipment(
    shipment: ShipmentCreate,
    service: ShipmentServiceDep,
) -> Shipment:
    return await service.add(shipment)


@router.get("/{field}")
async def get_shipment_field(
    field: str,
    id: int,
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
async def patch_shipment(
    id: int,
    shipment_update: ShipmentUpdate,
    service: ShipmentServiceDep,
) -> Shipment:
    update = shipment_update.model_dump(exclude_unset=True)
    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of the fields is required!",
        )
    shipment = await service.update(id, update)
    return shipment


@router.delete("/")
async def delete_shipment(
    id: int,
    service: ShipmentServiceDep,
) -> dict[str, Any]:
    await service.delete(id)
    return {"detail": f"Shipment with #{id} is deleted!"}
