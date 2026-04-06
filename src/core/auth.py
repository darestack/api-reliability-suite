from datetime import datetime, timedelta, UTC
from uuid import uuid4

import bcrypt
from jose import jwt

from src.core.config import settings

ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT token using the configured default expiry unless overridden."""
    to_encode = data.copy()
    token_ttl = (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    issued_at = datetime.now(UTC)
    expire = issued_at + token_ttl
    to_encode.setdefault("jti", str(uuid4()))
    to_encode.setdefault("typ", "access")
    to_encode.update({"exp": expire, "iat": issued_at})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def token_expiry_from_payload(payload: dict) -> datetime:
    return datetime.fromtimestamp(payload["exp"], UTC)


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()
