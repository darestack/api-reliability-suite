import asyncio
from contextlib import asynccontextmanager

from src.core.config import settings


_llm_bulkhead = asyncio.Semaphore(settings.LLM_MAX_CONCURRENCY)


@asynccontextmanager
async def llm_bulkhead():
    """Bound concurrent LLM requests to avoid a thundering herd."""
    async with _llm_bulkhead:
        yield
