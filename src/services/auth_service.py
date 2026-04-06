from datetime import timedelta
from typing import Optional

from jose import jwt
from fastapi import HTTPException
import structlog

from src.core.auth import (
    ALGORITHM,
    create_access_token as build_access_token,
    verify_password,
)
from src.core.config import settings
from src.infrastructure.user_repository import UserRepository
from src.domain.models import AuthenticatedUser, User

logger = structlog.get_logger()


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def authenticate_user(self, username: str, password: str) -> User | None:
        """
        Validates credentials using the repository.
        """
        user = await self.repository.get_user(username)
        if user is None or not user.is_active:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ):
        """
        Generates a JWT token.
        """
        return build_access_token(data=data, expires_delta=expires_delta)

    async def verify_token(self, token: str) -> AuthenticatedUser:
        """
        Decodes and validates a JWT token.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            user = await self.repository.get_user(username)
            if user is None or not user.is_active:
                raise HTTPException(status_code=401, detail="Invalid token")

            return AuthenticatedUser(username=user.username, role=user.role)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")
