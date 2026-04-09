import bcrypt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import SQLModel
from app.services.base import BaseService
from app.utils import generate_access_token

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


class UserService(BaseService):
    def __init__(self, model: type[SQLModel], session: AsyncSession):
        self.model = model
        self.session = session

    async def _add_user(self,data: dict):
        user = self.model(
            **data,
            password_hash=hash_password(data["password"]),
        )
        
        return await self._add(user)

    async def _get_by_email(self, email: str):
        return await self.session.scalar(select(self.model).where(self.model.email == email)) # type: ignore

    async def _generate_token(self, email, password) -> str:
        # Validate credentials
        user = await self._get_by_email(email)

        if user is None or not bcrypt.checkpw(
            password.encode("utf-8"),
            user.password_hash.encode("utf-8"),
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incorrect email or password",
            )
        return generate_access_token(
            data={
                "user": {
                    "name": user.name,
                    "id": str(user.id),
                }
            }
        )
       
