from datetime import timedelta
from uuid import UUID

import bcrypt
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlmodel import SQLModel
from app.services.base import BaseService
from app.services.notification import NotificationService
from app.utils import (
    decode_url_safe_token,
    generate_access_token,
    generate_url_safe_token,
)
from app.config import app_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


class UserService(BaseService):
    def __init__(
        self, model: type[SQLModel], session: AsyncSession, tasks: BackgroundTasks
    ):
        self.model = model
        self.session = session
        self.notification_service = NotificationService(tasks)

    async def _add_user(self, data: dict, router_prefix: str):
        user = self.model(
            **data,
            password_hash=hash_password(data["password"]),
        )
        user = await self._add(user)
        token = generate_url_safe_token(
            {
                "email": user.email,
                "id": str(user.id),
            }
        )
        await self.notification_service.send_email_with_template(
            recipients=[user.email],
            subject="Verify your Account with fastship",
            context={
                "username": user.name,
                "verification_url": f"http://{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}",
            },
            template_name="mail_email_verify.html",
        )

        return user

    async def verify_email(self, token: str):
        token_data = decode_url_safe_token(token)

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token",
            )
        user = await self._get(UUID(token_data["id"]))

        user.email_verified = True
        await self._update(user)

    async def _get_by_email(self, email: str):
        return await self.session.scalar(select(self.model).where(self.model.email == email))  # type: ignore

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

        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not verified",
            )

        return generate_access_token(
            data={
                "user": {
                    "name": user.name,
                    "id": str(user.id),
                }
            }
        )

    async def send_password_reset_link(self, email: str, router_prefix: str):
        user = await self._get_by_email(email)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user found with the given email",
            )

        token = generate_url_safe_token(
            {
                "id": str(user.id),
            },
            salt="password-reset",
        )

        await self.notification_service.send_email_with_template(
            recipients=[user.email],
            subject="Reset your password for fastship",
            context={
                "username": user.name,
                "reset_url": f"http://{app_settings.APP_DOMAIN}{router_prefix}/reset_password_form?token={token}",
            },
            template_name="mail_password_reset.html",
        )

    async def reset_password(self, token: str, password: str):
        token_data = decode_url_safe_token(
            token,
            salt="password-reset",
            expiry=timedelta(days=1),
        )
        
        if not token_data:
            return False
        
        user = await self._get(UUID(token_data["id"]))
        
        user.password_hash = hash_password(password)
        await self._update(user)
        return True
