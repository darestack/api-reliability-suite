from datetime import datetime, timedelta, UTC
import bcrypt
from jose import jwt
from src.core.config import settings

# JWT Config (We'll use a hardcoded secret for learning, but settings in prod)
# SECRET_KEY = "your-super-secret-key-change-this-in-prod"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT token using the configured default expiry unless overridden."""
    to_encode = data.copy()
    token_ttl = (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    expire = datetime.now(UTC) + token_ttl
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_password_hash(password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()
