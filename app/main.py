from time import perf_counter
from typing import Annotated
from uuid import UUID, uuid4
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Depends, FastAPI, Request, Response
from scalar_fastapi import get_scalar_api_reference

from app.api.router import master_router
from app.api.schemas.tag import APITag
from app.core.exceptions import add_exception_handlers
from app.worker.tasks import add_log

description = """
Delivery Managment system for sellers and delivery agents

### Seller
- Submit shipment effortlessly
- Share tracking links with customers

### Delivery Agent
- Auto accept shipment
- Trak and update shipments status
- Email and sms notification
"""

app = FastAPI(
    title="Fastship",
    description=description,
    docs_url=None,
    redoc_url=None,
    version="0.1.0",
    terms_of_service="https://fastship/terms/",
    contact={
        "name": "Fastship Support",
        "url": "https://fastship/support/",
        "emsil": "support@fastship.com",
    },
    openapi_tags=[
        {"name": APITag.SHIPMENT, "description": "Operations related to shipments",},
        {"name": APITag.SELLER, "description": "Operations related to seller"},
        {"name": APITag.PARTNER, "description": "Operations related to delivery partner"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5500"],
    allow_origins=["*"],
    allow_methods=["*"],
)

app.include_router(master_router)

# Add all exceptions handlers
add_exception_handlers(app)


@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    start = perf_counter()
    response: Response = await call_next(request)
    end = perf_counter()
    time_taken = round(end - start, 2)
    add_log.delay(
        f"{request.method} {request.url} ({response.status_code}) {time_taken} s"
    )
    return response

# Example Dependency
def get_id():
    return uuid4()

# Server Running Status
@app.get("/")
async def read_root(id: Annotated[UUID, Depends(get_id)]):
    return {"detail": str(id)}

### Scalar API Documentation
@app.get("/docs", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
