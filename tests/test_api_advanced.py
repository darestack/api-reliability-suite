import pytest
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch
import os

from jose import jwt

from src.core.auth import ALGORITHM
from src.core.config import settings


@pytest.mark.asyncio
async def test_summarize_errors_endpoint_success(client, auth_headers):
    """Test /debug/summarize-errors success path with mocked LLM"""
    # Create a dummy app.json
    log_content = '{"event": "error occurred", "level": "error"}\n'
    with open(settings.LOG_FILE_PATH, "w") as f:
        f.write(log_content)

    try:
        with patch(
            "src.main.summarize_with_llm", new_callable=AsyncMock
        ) as mock_summarize:
            mock_summarize.return_value = {
                "summary_text": "Mocked summary",
                "structured_insight": {
                    "root_cause_id": "test",
                    "severity": "LOW",
                    "action": ["none"],
                },
                "provider": "groq",
            }

            response = await client.get("/debug/summarize-errors", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert "ai_summary" in data
            assert data["ai_summary"]["summary_text"] == "Mocked summary"
            assert data["provider"] == "groq"
    finally:
        if os.path.exists(settings.LOG_FILE_PATH):
            os.remove(settings.LOG_FILE_PATH)


@pytest.mark.asyncio
async def test_summarize_errors_no_logs(client, auth_headers):
    """Test /debug/summarize-errors when log file is present but contains no errors"""
    with open(settings.LOG_FILE_PATH, "w") as f:
        f.write('{"event": "info message", "level": "info"}\n')

    try:
        response = await client.get("/debug/summarize-errors", headers=auth_headers)
        assert response.status_code == 200
        assert "No errors found" in response.json()["summary"]
        assert response.json()["provider"] is None
    finally:
        if os.path.exists(settings.LOG_FILE_PATH):
            os.remove(settings.LOG_FILE_PATH)


@pytest.mark.asyncio
async def test_summarize_errors_file_not_found(client, auth_headers):
    """Test /debug/summarize-errors when log file is missing"""
    if os.path.exists(settings.LOG_FILE_PATH):
        os.remove(settings.LOG_FILE_PATH)

    response = await client.get("/debug/summarize-errors", headers=auth_headers)
    assert response.status_code == 200
    assert "No log file found" in response.json()["summary"]
    assert response.json()["provider"] is None


@pytest.mark.asyncio
async def test_auth_service_authenticate_no_user():
    """Test AuthService when user does not exist (Coverage)"""
    from src.services.auth_service import AuthService
    from src.infrastructure.user_repository import user_repository

    service = AuthService(repository=user_repository)
    assert service.authenticate_user("non-existent", "password") is False


@pytest.mark.asyncio
async def test_auth_service_create_token_with_delta():
    """Test AuthService.create_access_token with custom expiration (Coverage)"""
    from src.services.auth_service import AuthService
    from src.infrastructure.user_repository import user_repository

    service = AuthService(repository=user_repository)
    token = service.create_access_token(
        data={"sub": "test"}, expires_delta=timedelta(minutes=5)
    )
    assert token is not None


@pytest.mark.asyncio
async def test_auth_service_default_token_uses_configured_expiry():
    """Default AuthService token expiry should follow ACCESS_TOKEN_EXPIRE_MINUTES."""
    from src.services.auth_service import AuthService
    from src.infrastructure.user_repository import user_repository

    service = AuthService(repository=user_repository)
    token = service.create_access_token(data={"sub": "test"})
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    expires_at = datetime.fromtimestamp(payload["exp"], UTC)
    remaining = expires_at - datetime.now(UTC)

    assert remaining <= timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES, seconds=5
    )
    assert remaining >= timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES - 1)


@pytest.mark.asyncio
async def test_auth_service_verify_token_no_sub():
    """Test AuthService.verify_token with payload missing 'sub' (Coverage)"""
    from src.services.auth_service import AuthService
    from src.infrastructure.user_repository import user_repository
    from jose import jwt
    from src.core.config import settings
    from src.core.auth import ALGORITHM

    service = AuthService(repository=user_repository)
    # Create token without 'sub'
    token = jwt.encode({"some": "payload"}, settings.SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(Exception):  # FastAPI HTTPException
        service.verify_token(token)
