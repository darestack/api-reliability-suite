import json
from typing import Any

import redis.asyncio as redis
import structlog

from src.core.config import settings

logger = structlog.get_logger()


class FallbackCache:
    """Redis-backed cache used for degraded fallback responses."""

    def __init__(self, cache_url: str | None):
        self.cache_url = cache_url
        self._client: redis.Redis | None = None

    def enabled(self) -> bool:
        return bool(self.cache_url)

    def _get_client(self) -> redis.Redis | None:
        if not self.cache_url:
            return None
        if self._client is None:
            self._client = redis.from_url(self.cache_url, decode_responses=True)
        return self._client

    async def get_json(self, key: str) -> dict[str, Any] | None:
        client = self._get_client()
        if client is None:
            return None

        try:
            payload = await client.get(key)
            if not payload:
                return None
            return json.loads(payload)
        except Exception as exc:
            logger.warning("fallback_cache_read_failed", key=key, error=str(exc))
            return None

    async def set_json(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
        client = self._get_client()
        if client is None:
            return

        try:
            await client.set(key, json.dumps(value), ex=ttl_seconds)
        except Exception as exc:
            logger.warning("fallback_cache_write_failed", key=key, error=str(exc))

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


fallback_cache = FallbackCache(settings.CIRCUIT_BREAKER_CACHE_URL)
