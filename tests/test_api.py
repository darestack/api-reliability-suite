import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app

@pytest.fixture
async def client():
  transport = ASGITransport(app=app)
  async with AsyncClient(transport=transport, base_url="http://test") as ac:
    yield ac

@pytest.mark.asyncio
async def test_health_check(client):
  response = await client.get("/health")
  assert response.status_code == 200
  assert response.json() == {"status": "ok", "service": "reliability-suite"}


@pytest.mark.asyncio
async def test_force_error_return_500(client):
  response = await client.get("/force-error")
  assert response.status_code == 500
  assert "error" in response.json()
  assert response.json()["error"] == "Internal Server Error"

@pytest.mark.asyncio
async def test_slow_endpoint(client):
  response = await client.get("/slow")
  assert response.status_code == 200
  assert response.json() == {"status": "done", "message": "That was slow!"}
  