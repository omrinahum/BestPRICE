import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import timedelta
from backend.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    get_current_user_id,
    require_current_user_id
)
from fastapi import HTTPException


def test_get_password_hash():
    """
    get_password_hash: creates a bcrypt hash
    """
    password = "MySecurePassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert len(hashed) > 20
    assert hashed.startswith("$2b$")


def test_verify_password_correct():
    """
    verify_password: returns True for correct password
    """
    password = "TestPassword456"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """
    verify_password: returns False for incorrect password
    """
    password = "TestPassword456"
    hashed = get_password_hash(password)
    
    assert verify_password("WrongPassword", hashed) is False


def test_create_access_token():
    """
    create_access_token: creates valid JWT token
    """
    data = {"sub": "123", "username": "testuser"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 50
    assert token.count(".") == 2  # JWT has 3 parts separated by dots


def test_verify_token_valid():
    """
    verify_token: decodes valid token
    """
    data = {"sub": "789", "username": "user"}
    token = create_access_token(data)
    
    payload = verify_token(token)
    
    assert payload is not None
    assert payload["sub"] == "789"
    assert payload["username"] == "user"


def test_verify_token_invalid():
    """
    verify_token: returns None for invalid token
    """
    invalid_token = "invalid.jwt.token"
    
    payload = verify_token(invalid_token)
    
    assert payload is None


def test_verify_token_expired():
    """
    verify_token: returns None for expired token
    """
    data = {"sub": "999"}
    # Create token that expires immediately
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    
    payload = verify_token(token)
    
    assert payload is None


@pytest.mark.asyncio
async def test_get_current_user_id_valid():
    """
    get_current_user_id: extracts user ID from valid token
    """
    data = {"sub": "42", "username": "testuser"}
    token = create_access_token(data)
    
    credentials = MagicMock()
    credentials.credentials = token
    
    user_id = await get_current_user_id(credentials)
    
    assert user_id == 42


@pytest.mark.asyncio
async def test_get_current_user_id_invalid():
    """
    get_current_user_id: returns None for invalid token
    """
    credentials = MagicMock()
    credentials.credentials = "invalid.token"
    
    user_id = await get_current_user_id(credentials)
    
    assert user_id is None


@pytest.mark.asyncio
async def test_require_current_user_id_valid():
    """
    require_current_user_id: returns user ID for valid token
    """
    data = {"sub": "100"}
    token = create_access_token(data)
    
    credentials = MagicMock()
    credentials.credentials = token
    
    user_id = await require_current_user_id(credentials)
    
    assert user_id == 100


@pytest.mark.asyncio
async def test_require_current_user_id_invalid():
    """
    require_current_user_id: raises HTTPException for invalid token
    """
    credentials = MagicMock()
    credentials.credentials = "bad.token"
    
    with pytest.raises(HTTPException) as exc_info:
        await require_current_user_id(credentials)
    
    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail
