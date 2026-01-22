import httpx
import structlog
from typing import Optional, Dict, Any
from opentelemetry import propagate
from src.core.middleware import correlation_id_ctx

logger = structlog.get_logger()


class InstrumentedHttpClient:
    """
    HTTP Client that automatically propagates:
    1. OpenTelemetry Trace Context
    2. Custom Correlation ID (from middleware context)
    """

    def __init__(self, timeout: float = 10.0):
        self.client = httpx.AsyncClient(timeout=timeout)

    async def get(
        self, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> httpx.Response:
        return await self._request("GET", url, headers=headers, **kwargs)

    async def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> httpx.Response:
        return await self._request("POST", url, json=json, headers=headers, **kwargs)

    async def _request(
        self, method: str, url: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> httpx.Response:
        headers = headers or {}

        # 1. Propagate OpenTelemetry Trace Context (W3C Traceparent)
        propagate.inject(headers)

        # 2. Propagate our local Correlation ID
        corr_id = correlation_id_ctx.get()
        if corr_id:
            headers["X-Correlation-ID"] = corr_id

        logger.info("outgoing_request", method=method, url=url, correlation_id=corr_id)

        try:
            response = await self.client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(
                "outgoing_request_failed",
                method=method,
                url=url,
                error=str(e),
                correlation_id=corr_id,
            )
            raise

    async def close(self):
        await self.client.aclose()


# Singleton instance for standard use
http_client = InstrumentedHttpClient()
