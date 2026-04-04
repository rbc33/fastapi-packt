from typing import Any

from fastapi import FastAPI, HTTPException, status
from scalar_fastapi import get_scalar_api_reference

from .schemas import (
    ShipmentCreate,
    ShipmentRead,
    ShipmentUpdate,
)
from .database import Database

app = FastAPI()

db = Database()

@app.get("/shipment/latest", response_model=ShipmentRead)
def get_latest_shipment():
    shipment = db.get_last()
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shipments found"
        )
    return shipment
    

# @app.get("/shipment/{id}")
# def get_shipment(id: int)-> dict[str, Any]:
#     if id not in shipments:
#         return {"details": "Given id doesnt exist!"}
#     return shipments[id]

@app.get("/shipment", response_model=ShipmentRead)
def get_shipment(id: int):
    shipment = db.get(id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesnt exist!"
        )
    return shipment



@app.post("/shipment", response_model=None)
def submit_shipment(shipment: ShipmentCreate) -> dict[str, int]:
    new_id = db.create(shipment)
    return {"id": new_id}


@app.get("/shipment/{field}", response_model=ShipmentRead)
def get_shipment_field(field: str, id: int)-> Any:
    shipment = db.get(id)
    if not shipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Given id doesnt exist!"
        )
    if field not in shipment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field doesn't exist"
        )
    return shipment[field]

# @app.put("/shipment")
# def shipment_update(id: int, data: dict[str, Any])-> dict[str,Any]:
#     content = data.get("content")
#     weight = data.get("weight")
#     status = data.get("status") 
#     shipments[id] = {
#         "content": content,
#         "weight": weight,
#         "status": status
#     }
#     return shipments[id]



@app.patch("/shipment", response_model=ShipmentRead)
def patch_shipment(id: int, body: ShipmentUpdate):
    new_shipment = db.update(id, body)
    return new_shipment

@app.delete("/shipment")
def delete_shipment(id: int) -> dict[str, Any]:
    db.delete(id)
    return { "detail": f"Shipment with #{id} is deleted!"} 

@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"

    )
