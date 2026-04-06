from datetime import UTC, datetime, timedelta
from typing import Optional

from fastapi import HTTPException
import structlog

from src.core.auth import (
    create_access_token as build_access_token,
    decode_token,
    token_expiry_from_payload,
    verify_password,
)
from src.core.config import settings
from src.domain.models import AuthenticatedUser, TokenPair, User
from src.infrastructure.session_repository import SessionRepository, session_repository
from src.infrastructure.user_repository import UserRepository

logger = structlog.get_logger()


class AuthService:
    def __init__(
        self,
        repository: UserRepository,
        session_store: SessionRepository = session_repository,
    ):
        self.repository = repository
        self.session_store = session_store

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

    async def create_token_pair(
        self, user: User, *, family_id: str | None = None
    ) -> TokenPair:
        if user.id is None:
            raise ValueError("Persistent user id is required to create a session")

        (
            refresh_token,
            refresh_session,
        ) = await self.session_store.create_refresh_session(
            user_id=user.id,
            family_id=family_id,
            expires_in=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        access_token = self.create_access_token(
            data={
                "sub": user.username,
                "role": user.role,
                "sid": refresh_session.id,
            }
        )
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def rotate_refresh_token(self, refresh_token: str) -> TokenPair:
        refresh_session = await self.session_store.get_refresh_session(refresh_token)
        if refresh_session is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if refresh_session.revoked_at is not None:
            await self.session_store.revoke_refresh_family(refresh_session.family_id)
            raise HTTPException(
                status_code=401, detail="Refresh token has been revoked"
            )

        if refresh_session.expires_at <= datetime.now(UTC):
            await self.session_store.revoke_refresh_token(refresh_token)
            raise HTTPException(status_code=401, detail="Refresh token has expired")

        user = await self.repository.get_user_by_id(refresh_session.user_id)
        if user is None or not user.is_active:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        replacement = await self.create_token_pair(
            user, family_id=refresh_session.family_id
        )
        replacement_session = await self.session_store.get_refresh_session(
            replacement.refresh_token
        )
        if replacement_session is None:
            raise HTTPException(status_code=500, detail="Refresh token rotation failed")

        await self.session_store.mark_refresh_session_rotated(
            refresh_session.id, replaced_by_token_id=replacement_session.id
        )
        return replacement

    async def verify_token(self, token: str) -> AuthenticatedUser:
        """
        Decodes and validates a JWT token.
        """
        try:
            payload = decode_token(token)
            username: str = payload.get("sub")
            token_type: str | None = payload.get("typ")
            token_id: str | None = payload.get("jti")
            if username is None or token_type != "access" or token_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")

            if await self.session_store.is_access_token_revoked(token_id):
                raise HTTPException(status_code=401, detail="Token has been revoked")

            user = await self.repository.get_user(username)
            if user is None or not user.is_active:
                raise HTTPException(status_code=401, detail="Invalid token")

            return AuthenticatedUser(id=user.id, username=user.username, role=user.role)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

    async def revoke_access_token(self, token: str) -> None:
        payload = decode_token(token)
        token_id: str | None = payload.get("jti")
        username: str | None = payload.get("sub")
        if token_id is None or username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        await self.session_store.revoke_access_token(
            jti=token_id,
            username=username,
            expires_at=token_expiry_from_payload(payload),
        )

    async def logout(
        self, *, access_token: str, refresh_token: str | None = None
    ) -> None:
        await self.revoke_access_token(access_token)
        if refresh_token:
            await self.session_store.revoke_refresh_token(refresh_token)
