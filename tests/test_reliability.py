import pytest
import uuid
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_correlation_id_propagation(client):
    """Verify that X-Correlation-ID is generated and returned"""
    response = await client.get("/health")
    assert "X-Correlation-ID" in response.headers
    correlation_id = response.headers["X-Correlation-ID"]
    # Should be a valid UUID
    uuid.UUID(correlation_id)


@pytest.mark.asyncio
async def test_custom_correlation_id(client):
    """Verify that we can pass our own Correlation ID"""
    custom_id = "test-corr-id-123"
    response = await client.get("/health", headers={"X-Correlation-ID": custom_id})
    assert response.headers["X-Correlation-ID"] == custom_id


@pytest.mark.asyncio
async def test_circuit_breaker_flow(client):
    """Verify circuit breaker trips and returns fallback"""
    from src.core.circuit_breaker import external_api_breaker

    # Ensure breaker is closed before starting
    external_api_breaker.close()

    # 1. Enable failure simulation
    await client.post("/simulate-failure/true")

    # 2. Hit it until it trips (threshold is 5)
    # The endpoint should return 502 Bad Gateway during failures, eventually 200 (Fallback)
    circuit_opened = False
    for i in range(7):
        resp = await client.get("/external-api")

        if resp.status_code == 502:
            # Still failing, circuit closed
            continue
        elif resp.status_code == 200:
            # Circuit might have opened
            data = resp.json()
            if data.get("source") == "fallback":
                circuit_opened = True
                break
            else:
                assert False, f"Iteration {i + 1}: got 200 OK (success) but expected failure/fallback. Body: {data}"
        else:
            assert False, f"Iteration {i + 1}: Unexpected status {resp.status_code}"

    assert circuit_opened, "Circuit did not open after 7 failed attempts"

    # 3. Verify it stays open
    resp = await client.get("/external-api")
    assert resp.status_code == 200
    assert resp.json()["source"] == "fallback"

    # 4. Reset
    await client.post("/simulate-failure/false")
    external_api_breaker.close()


@pytest.mark.asyncio
async def test_auth_service_invalid_token(client):
    """Verify AuthService handles invalid tokens correctly (Coverage)"""
    from src.services.auth_service import AuthService
    from src.infrastructure.user_repository import user_repository

    service = AuthService(repository=user_repository)

    with pytest.raises(Exception):  # FastAPI HTTPException
        await service.verify_token("invalid-token-123")


@pytest.mark.asyncio
async def test_ai_summarize_no_token(client):
    """Test AI endpoint rejects unauthenticated (Coverage)"""
    response = await client.get("/debug/summarize-errors")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_slo_report_without_prometheus_returns_targets(client):
    response = await client.get("/slo/report")
    assert response.status_code == 200
    data = response.json()
    assert data["targets"]["success_ratio"] == 0.99
    assert data["metrics"] is None


@pytest.mark.asyncio
async def test_readiness_report_defaults_to_ok(client):
    response = await client.get("/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["dependencies"]["database"]["status"] == "ok"
    assert payload["dependencies"]["llm_provider"]["status"] in {
        "skipped",
        "configured",
        "ok",
    }


@pytest.mark.asyncio
async def test_readiness_report_can_be_degraded_without_failing_traffic(client):
    with patch(
        "src.main.build_readiness_report",
        new=AsyncMock(
            return_value=(
                200,
                {
                    "status": "degraded",
                    "dependencies": {
                        "database": {"status": "ok", "required": True},
                        "llm_provider": {
                            "status": "error",
                            "required": False,
                            "provider": "groq",
                        },
                    },
                },
            )
        ),
    ):
        response = await client.get("/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "degraded"
    assert payload["dependencies"]["llm_provider"]["status"] == "error"


@pytest.mark.asyncio
async def test_readiness_report_returns_503_for_required_dependency_failure(client):
    with patch(
        "src.main.build_readiness_report",
        new=AsyncMock(
            return_value=(
                503,
                {
                    "status": "error",
                    "dependencies": {
                        "database": {"status": "error", "required": True},
                    },
                },
            )
        ),
    ):
        response = await client.get("/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "error"


@pytest.mark.asyncio
async def test_circuit_breaker_uses_cached_fallback_when_available(client):
    from src.core.circuit_breaker import external_api_breaker

    external_api_breaker.open()

    with patch(
        "src.main.fallback_cache.get_json",
        new=AsyncMock(
            return_value={
                "status": "ok",
                "message": "Cached success",
                "source": "upstream",
            }
        ),
    ):
        response = await client.get("/external-api")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["source"] == "fallback_cache"

    external_api_breaker.close()
