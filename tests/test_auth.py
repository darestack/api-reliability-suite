from src.core.auth import get_password_hash, verify_password, create_access_token


def test_password_hashing():
    """Verify password hashing and verification works"""
    password = "secret-blueprint-2026"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_token_generation():
    """Verify access token can be generated"""
    token = create_access_token({"sub": "test-user"})
    assert isinstance(token, str)
    assert len(token) > 20
