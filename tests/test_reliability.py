import pytest
import uuid


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
            if data.get("source") == "cache":
                circuit_opened = True
                break
            else:
                assert False, f"Iteration {i+1}: got 200 OK (success) but expected failure/fallback. Body: {data}"
        else:
            assert False, f"Iteration {i+1}: Unexpected status {resp.status_code}"

    assert circuit_opened, "Circuit did not open after 7 failed attempts"

    # 3. Verify it stays open
    resp = await client.get("/external-api")
    assert resp.status_code == 200
    assert resp.json()["source"] == "cache"

    # 4. Reset
    await client.post("/simulate-failure/false")
    external_api_breaker.close()


@pytest.mark.asyncio
async def test_auth_service_invalid_token():
    """Verify AuthService handles invalid tokens correctly (Coverage)"""
    from src.services.auth_service import AuthService
    from src.infrastructure.user_repository import user_repository

    service = AuthService(repository=user_repository)

    with pytest.raises(Exception):  # FastAPI HTTPException
        service.verify_token("invalid-token-123")


@pytest.mark.asyncio
async def test_ai_summarize_no_token(client):
    """Test AI endpoint rejects unauthenticated (Coverage)"""
    response = await client.get("/debug/summarize-errors")
    assert response.status_code == 401
