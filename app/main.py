from time import perf_counter
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, Request, Response
from scalar_fastapi import get_scalar_api_reference

from app.api.router import master_router
from app.core.exceptions import add_exception_handlers
from app.worker.tasks import add_log

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:5500"],
    allow_origins=["*"],
    allow_methods=["*"]
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


### Scalar API Documentation
@app.get("/scalar", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Scalar API",
    )
