from __future__ import annotations

from urllib.parse import urlparse

import redis.asyncio as redis

from src.core.config import settings
from src.core.llm import LLMFactory
from src.infrastructure.database import database_is_ready
from src.infrastructure.fallback_cache import fallback_cache


async def build_readiness_report() -> tuple[int, dict]:
    """Return an HTTP status code plus a dependency-aware readiness report."""
    dependencies: dict[str, dict[str, object]] = {}
    overall_status = "ok"
    http_status = 200

    database_ready = await database_is_ready()
    dependencies["database"] = {
        "status": "ok" if database_ready else "error",
        "required": True,
    }
    if not database_ready:
        overall_status = "error"
        http_status = 503

    rate_limit_dependency = await _check_optional_redis_dependency(
        settings.RATE_LIMIT_STORAGE_URI
    )
    dependencies["rate_limit_store"] = rate_limit_dependency
    if rate_limit_dependency["required"] and rate_limit_dependency["status"] == "error":
        overall_status = "error"
        http_status = 503

    fallback_dependency = await _check_optional_cache_dependency()
    dependencies["fallback_cache"] = fallback_dependency
    if fallback_dependency["required"] and fallback_dependency["status"] == "error":
        overall_status = "error"
        http_status = 503

    llm_dependency = await LLMFactory.check_provider_health()
    dependencies["llm_provider"] = llm_dependency
    if overall_status == "ok" and llm_dependency["status"] == "error":
        overall_status = "degraded"

    return http_status, {"status": overall_status, "dependencies": dependencies}


async def _check_optional_cache_dependency() -> dict[str, object]:
    if not fallback_cache.enabled():
        return {"status": "skipped", "required": False}

    ready = await fallback_cache.ping()
    return {"status": "ok" if ready else "error", "required": True}


async def _check_optional_redis_dependency(storage_uri: str) -> dict[str, object]:
    parsed = urlparse(storage_uri)
    if parsed.scheme != "redis":
        return {"status": "skipped", "required": False}

    client = redis.from_url(storage_uri, decode_responses=True)
    try:
        ready = bool(await client.ping())
        return {"status": "ok" if ready else "error", "required": True}
    except Exception:
        return {"status": "error", "required": True}
    finally:
        await client.aclose()
