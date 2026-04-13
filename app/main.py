from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference

from app.api.router import master_router

#from .database import Database
from .database.session import create_db_table


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    await create_db_table()
    yield


app = FastAPI(lifespan=lifespan_handler)

app.include_router(master_router)

class UpperResponse(Response):
    def __init__(self, content = None, status_code = 200, headers = None, media_type = None, background = None):
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content):
        content = content.upper()
        return super().render(content)

### Custom response
@app.get("/custom", response_class=JSONResponse, response_model=dict[str,Any])
def get_custom_response():
    return ({
            "detail": "json response",
            "timestamp": datetime.now(),

    })


@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API"

    )

