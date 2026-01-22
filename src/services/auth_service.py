from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from src.core.auth import verify_password, ALGORITHM
from src.core.config import settings
from fastapi import HTTPException
import structlog

from src.infrastructure.user_repository import UserRepository

logger = structlog.get_logger()


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Validates credentials using the repository.
        """
        user_hash = self.repository.get_user_hash(username)
        if not user_hash:
            return False

        return verify_password(password, user_hash)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ):
        """
        Generates a JWT token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str):
        """
        Decodes and validates a JWT token.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            return username
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")
