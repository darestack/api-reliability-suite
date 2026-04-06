import os
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.core.config import settings

# The Limiter
# - get_remote_address: Uses the client's IP to track limits.
# - enabled: Can be toggled for testing or maintenance.
limiter = Limiter(
    key_func=get_remote_address,
    enabled=os.getenv("TESTING", "false").lower() != "true",
    headers_enabled=settings.RATE_LIMIT_HEADERS_ENABLED,
    storage_uri=settings.RATE_LIMIT_STORAGE_URI,
    in_memory_fallback_enabled=settings.RATE_LIMIT_IN_MEMORY_FALLBACK_ENABLED,
    key_prefix=settings.RATE_LIMIT_KEY_PREFIX,
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    response = JSONResponse(
        {"error": f"Rate limit exceeded: {exc.detail}"},
        status_code=429,
    )
    current_limit = getattr(request.state, "view_rate_limit", None)
    if current_limit is not None:
        request.app.state.limiter._inject_headers(response, current_limit)
    return response
