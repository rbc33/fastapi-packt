import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.seller import SellerCreate
from app.database.models import Seller


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
        
