import os
from importlib import import_module
from unittest.mock import MagicMock

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from opentelemetry import trace

os.environ["DEBUG"] = "false"
os.environ["OTLP_ENDPOINT"] = ""
os.environ["LOG_FILE_PATH"] = "test_app.json"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_data/reliability_suite_test.db"
os.environ["SEED_DEMO_USER"] = "true"


@pytest.fixture(autouse=True)
def mock_otlp_exporter(monkeypatch):
    """
    Prevents tests from trying to connect to Jaeger.
    Mocks OTLPSpanExporter to do nothing.
    """
    tracing = import_module("src.core.tracing")
    monkeypatch.setattr(tracing, "configure_tracing", lambda app: None)
    monkeypatch.setattr("src.core.tracing.OTLPSpanExporter", MagicMock())


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter = import_module("src.core.rate_limit").limiter
    reset = getattr(getattr(limiter, "_storage", None), "reset", None)
    if callable(reset):
        reset()
    yield
    if callable(reset):
        reset()


@pytest.fixture
async def client():
    """
    Creates an async test client for our FastAPI app.
    raise_app_exceptions=False makes 500 responses observable to tests.
    """
    app = import_module("src.main").app
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as c:
            yield c
    if os.path.exists("test_app.json"):
        os.remove("test_app.json")
    if os.path.exists("test_data/reliability_suite_test.db"):
        os.remove("test_data/reliability_suite_test.db")
    shutdown = getattr(trace.get_tracer_provider(), "shutdown", None)
    if callable(shutdown):
        shutdown()


@pytest.fixture
def auth_headers():
    """Returns headers with a valid JWT token for 'demo' user."""
    from src.core.auth import create_access_token

    token = create_access_token(data={"sub": "demo", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}
