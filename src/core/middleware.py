import uuid
import structlog
from contextvars import ContextVar
from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

# ContextVar to store correlation_id for the current request
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIdMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        correlation_id = Headers(scope=scope).get("X-Correlation-ID", str(uuid.uuid4()))
        token = correlation_id_ctx.set(correlation_id)
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        async def send_with_correlation_id(message: Message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Correlation-ID"] = correlation_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_correlation_id)
        finally:
            correlation_id_ctx.reset(token)
            structlog.contextvars.unbind_contextvars("correlation_id")
