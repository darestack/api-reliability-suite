from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from uuid import uuid4

from sqlalchemy import delete, select

from src.infrastructure.database import AsyncSessionFactory
from src.infrastructure.session_models import (
    RefreshTokenTable,
    RevokedAccessTokenTable,
)


def _hash_refresh_token(token: str) -> str:
    return sha256(token.encode()).hexdigest()


@dataclass(slots=True)
class RefreshSession:
    id: str
    user_id: int
    family_id: str
    expires_at: datetime
    revoked_at: datetime | None
    replaced_by_token_id: str | None


class SessionRepository:
    """Persistence layer for refresh-session rotation and access-token revocation."""

    def __init__(self, session_factory=AsyncSessionFactory):
        self.session_factory = session_factory

    async def create_refresh_session(
        self,
        *,
        user_id: int,
        expires_in: timedelta,
        family_id: str | None = None,
    ) -> tuple[str, RefreshSession]:
        raw_token = token_urlsafe(48)
        now = datetime.now(UTC)
        family = family_id or str(uuid4())
        record = RefreshTokenTable(
            user_id=user_id,
            token_hash=_hash_refresh_token(raw_token),
            family_id=family,
            expires_at=now + expires_in,
            created_at=now,
            last_used_at=now,
        )
        async with self.session_factory() as session:
            session.add(record)
            await session.commit()
            await session.refresh(record)
        return raw_token, self._to_refresh_session(record)

    async def get_refresh_session(self, raw_token: str) -> RefreshSession | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(RefreshTokenTable).where(
                    RefreshTokenTable.token_hash == _hash_refresh_token(raw_token)
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                return None
            return self._to_refresh_session(record)

    async def mark_refresh_session_rotated(
        self, token_id: str, *, replaced_by_token_id: str
    ) -> None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(RefreshTokenTable).where(RefreshTokenTable.id == token_id)
            )
            record = result.scalar_one_or_none()
            if record is None:
                return
            record.revoked_at = datetime.now(UTC)
            record.replaced_by_token_id = replaced_by_token_id
            await session.commit()

    async def revoke_refresh_token(self, raw_token: str) -> None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(RefreshTokenTable).where(
                    RefreshTokenTable.token_hash == _hash_refresh_token(raw_token)
                )
            )
            record = result.scalar_one_or_none()
            if record is None:
                return
            if record.revoked_at is None:
                record.revoked_at = datetime.now(UTC)
                await session.commit()

    async def revoke_refresh_family(self, family_id: str) -> None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(RefreshTokenTable).where(
                    RefreshTokenTable.family_id == family_id
                )
            )
            now = datetime.now(UTC)
            for record in result.scalars():
                if record.revoked_at is None:
                    record.revoked_at = now
            await session.commit()

    async def revoke_access_token(
        self, *, jti: str, username: str, expires_at: datetime
    ) -> None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(RevokedAccessTokenTable).where(
                    RevokedAccessTokenTable.jti == jti
                )
            )
            existing = result.scalar_one_or_none()
            if existing is None:
                session.add(
                    RevokedAccessTokenTable(
                        jti=jti,
                        username=username,
                        expires_at=expires_at,
                    )
                )
                await session.commit()

    async def is_access_token_revoked(self, jti: str) -> bool:
        async with self.session_factory() as session:
            await self._prune_revoked_access_tokens(session)
            result = await session.execute(
                select(RevokedAccessTokenTable).where(
                    RevokedAccessTokenTable.jti == jti
                )
            )
            return result.scalar_one_or_none() is not None

    async def prune_expired_refresh_sessions(self) -> None:
        async with self.session_factory() as session:
            now = datetime.now(UTC)
            await session.execute(
                delete(RefreshTokenTable).where(RefreshTokenTable.expires_at < now)
            )
            await self._prune_revoked_access_tokens(session)
            await session.commit()

    async def _prune_revoked_access_tokens(self, session) -> None:
        now = datetime.now(UTC)
        await session.execute(
            delete(RevokedAccessTokenTable).where(
                RevokedAccessTokenTable.expires_at < now
            )
        )

    @staticmethod
    def _to_refresh_session(record: RefreshTokenTable) -> RefreshSession:
        expires_at = record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return RefreshSession(
            id=record.id,
            user_id=record.user_id,
            family_id=record.family_id,
            expires_at=expires_at,
            revoked_at=record.revoked_at,
            replaced_by_token_id=record.replaced_by_token_id,
        )


session_repository = SessionRepository()
