from datetime import datetime, timedelta, UTC
from jose import jwt
from passlib.context import CryptContext
from src.core.config import settings

# 1. Setup Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 2. JWT Config (We'll use a hardcoded secret for learning, but settings in prod)
# SECRET_KEY = "your-super-secret-key-change-this-in-prod"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

ALGORITHM = "HS256"


def create_access_token(data: dict):
    """Creates a JWT token that expires in 30 minutes"""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)