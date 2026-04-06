from collections.abc import AsyncIterator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.infrastructure.db_base import Base


def _build_engine():
    database_url = settings.DATABASE_URL
    connect_args: dict[str, object] = {}

    if database_url.startswith("sqlite+aiosqlite:///"):
        database_path = database_url.removeprefix("sqlite+aiosqlite:///")
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        connect_args["timeout"] = 30

    return create_async_engine(
        database_url,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


engine = _build_engine()
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Yield a managed async database session."""
    async with AsyncSessionFactory() as session:
        yield session


async def init_database() -> None:
    """Create the current schema for local/dev use."""
    # Import models here so metadata is fully populated before create_all.
    from src.infrastructure.user_models import UserTable  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def close_database() -> None:
    """Dispose of the async engine cleanly."""
    await engine.dispose()
