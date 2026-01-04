import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import MagicMock
from src.main import app
from opentelemetry import trace


@pytest.fixture(autouse=True)
def mock_otlp_exporter(monkeypatch):
    """
    Prevents tests from trying to connect to Jaeger.
    Mocks OTLPSpanExporter to do nothing.
    """
    monkeypatch.setattr("src.core.tracing.OTLPSpanExporter", MagicMock())


@pytest.fixture(scope="session", autouse=True)
async def client():
    """
    Creates an async test client for our FastAPI app.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    trace.get_tracer_provider().shutdown()
