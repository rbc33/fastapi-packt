from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.services.notification import NotificationService

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

@app.get("/mail")
async def send_mail(task: BackgroundTasks):

    task.add_task(NotificationService().send_email,
        subject="Test Email",
        body="This is a test email sent from FastAPI using FastMail.",
        recipients=["xifof43652@nyspring.com"]
        )
    
    # await NotificationService().send_email(
    #     subject="Test Email",
    #     body="This is a test email sent from FastAPI using FastMail.",
    #     recipients=["xifof43652@nyspring.com"]
    #     )
    return {"detail": "Email sent successfully!"}