import bcrypt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.seller import SellerCreate
from app.database.models import Seller
from app.utils import generate_access_token


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


class SellerService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, credentials: SellerCreate):
        seller = Seller(
            **credentials.model_dump(exclude={"password"}),
            password_hash=hash_password(credentials.password),
        )
        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)

        return seller
    
    async def token(self, email, password)-> str:
        # Validate credentials
        result = await self.session.execute(
            select(Seller).where(Seller.email == email)
        )
        seller = result.scalar_one_or_none()

        if seller is None or not bcrypt.checkpw(password.encode("utf-8"), seller.password_hash.encode("utf-8")):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incorrect email or password",
            )
        token = generate_access_token(data={
            "user": {
                "name": seller.name,
                "id": seller.id,

            }
        })
        return token

