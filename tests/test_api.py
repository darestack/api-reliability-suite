import pytest

# --- Health & Error Tests ---


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_force_error_returns_500(client):
    response = await client.get("/force-error")
    assert response.status_code == 500
    assert "error" in response.json()
    assert response.json()["error"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_slow_endpoint(client):
    response = await client.get("/slow")
    assert response.status_code == 200
    assert response.json()["message"] == "That was slow!"


# --- Authentication Tests ---


@pytest.mark.asyncio
async def test_login_success(client):
    """Test successful login returns a JWT token"""
    response = await client.post(
        "/login", data={"username": "demo", "password": "secret123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Test login with wrong password fails"""
    response = await client.post(
        "/login", data={"username": "demo", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"


@pytest.mark.asyncio
async def test_protected_without_token(client):
    """Test protected route rejects unauthenticated requests"""
    response = await client.get("/protected")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_with_valid_token(client):
    """Test protected route accepts valid JWT token"""
    # First, get a token
    login_response = await client.post(
        "/login", data={"username": "demo", "password": "secret123"}
    )
    token = login_response.json()["access_token"]

    # Use the token to access protected route
    response = await client.get(
        "/protected", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Hello demo, you are authorized!" in response.json()["message"]
    assert response.json()["role"] == "admin"


# --- Rate Limiting Tests ---


@pytest.mark.asyncio
async def test_health_rate_limit(client):
    """Test that /health is rate limited after 5 requests"""
    # We already had one request from test_health_check, but let's be safe
    # and hit it 6 more times.
    for _ in range(6):
        response = await client.get("/health")

    assert response.status_code == 429
    assert "Rate limit exceeded" in response.text


@pytest.mark.asyncio
async def test_login_rate_limit(client):
    """Test that /login is rate limited after 5 requests"""
    for _ in range(6):
        response = await client.post(
            "/login", data={"username": "demo", "password": "wrongpassword"}
        )

    assert response.status_code == 429
    assert "Rate limit exceeded" in response.text
