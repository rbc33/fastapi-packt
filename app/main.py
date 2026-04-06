from contextlib import asynccontextmanager

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

#from .database import Database
from .database.session import create_db_table
from app.api.router import master_router


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_table()
    yield


app = FastAPI(lifespan=lifespan_handler)

app.include_router(master_router)

# db = Database()


# @app.get("/shipment/{id}")
# def get_shipment(id: int)-> dict[str, Any]:
#     if id not in shipments:
#         return {"details": "Given id doesnt exist!"}
#     return shipments[id]


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"

    )
