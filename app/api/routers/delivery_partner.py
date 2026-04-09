from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import SellerServiceDep,  get_partner_access_token
from app.api.schemas.delivery_partner import DeliveryPartnerCreate, DeliveryPartnerRead, DeliveryPartnerUpdate
from app.database.redis import add_jti_to_blacklist


router = APIRouter(prefix="/seller", tags=["Delivery Partner"])


## SIGN UP
@router.post("/partner", response_model=DeliveryPartnerRead)
async def register_delivery_partner(
    seller: DeliveryPartnerCreate,
    service,
):
    return await service.add(seller)


## LOGIN
@router.post("/token")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service,
):
    token = await service.token(request_form.username, request_form.password)

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.post("/")
async def update_delivery_partner(
    partner_update: DeliveryPartnerUpdate,
    partner: DeliveryPartnerUpdate,
    service,
):
    pass

# Logout
@router.get("/logout")
async def logout_delivery_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)],
):
    await add_jti_to_blacklist(token_data["jti"])
    return {
        "detail": "Succesfully logged out"
    }
