from datetime import UTC, datetime

from sqlalchemy import select

from src.core.config import settings
from src.domain.models import User, UserRole
from src.infrastructure.database import AsyncSessionFactory
from src.infrastructure.user_models import UserTable


def _to_domain_user(record: UserTable) -> User:
    return User(
        username=record.username,
        hashed_password=record.hashed_password,
        role=record.role,
        is_active=record.is_active,
    )


class UserRepository:
    """Async user repository backed by SQLAlchemy."""

    def __init__(self, session_factory=AsyncSessionFactory):
        self.session_factory = session_factory

    async def get_user(self, username: str) -> User | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(UserTable).where(UserTable.username == username)
            )
            record = result.scalar_one_or_none()
            if record is None:
                return None
            return _to_domain_user(record)

    async def upsert_user(
        self,
        username: str,
        password: str,
        role: UserRole = UserRole.USER,
        *,
        is_active: bool = True,
    ) -> User:
        from src.core.auth import get_password_hash

        async with self.session_factory() as session:
            result = await session.execute(
                select(UserTable).where(UserTable.username == username)
            )
            record = result.scalar_one_or_none()

            if record is None:
                record = UserTable(
                    username=username,
                    hashed_password=get_password_hash(password),
                    role=role,
                    is_active=is_active,
                )
                session.add(record)
            else:
                record.hashed_password = get_password_hash(password)
                record.role = role
                record.is_active = is_active
                record.updated_at = datetime.now(UTC)

            await session.commit()
            await session.refresh(record)
            return _to_domain_user(record)

    async def ensure_demo_user(self) -> None:
        if not settings.SEED_DEMO_USER:
            return

        role = UserRole(settings.DEMO_USER_ROLE)
        existing = await self.get_user(settings.DEMO_USERNAME)
        if existing is not None:
            return

        await self.upsert_user(
            username=settings.DEMO_USERNAME,
            password=settings.DEMO_PASSWORD,
            role=role,
            is_active=True,
        )


user_repository = UserRepository()
