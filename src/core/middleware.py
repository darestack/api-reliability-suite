import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
from contextvars import ContextVar

# ContextVar to store correlation_id for the current request
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Get correlation_id from header or generate new one
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

        # 2. Set the context variable
        token = correlation_id_ctx.set(correlation_id)

        # 3. Add to structlog context
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        try:
            response = await call_next(request)
            # 4. Return the ID in the response headers
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            # 5. Clean up
            correlation_id_ctx.reset(token)
            structlog.contextvars.unbind_contextvars("correlation_id")
