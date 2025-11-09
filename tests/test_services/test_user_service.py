import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.user_service import UserService
from backend.schemas.user_schema import UserCreate
from backend.models.users import User
from backend.utils.error import ValidationError, NotFoundError


@pytest.mark.asyncio
async def test_create_user_success():
    """
    create_user: successfully creates a new user
    """
    service = UserService()
    service.get_user_by_username = AsyncMock(return_value=None)
    service.get_user_by_email = AsyncMock(return_value=None)
    
    session = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.commit = AsyncMock()
    
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="SecurePass123",
        full_name="Test User"
    )
    
    with patch('backend.services.user_service.get_password_hash', return_value="hashed_password"):
        user = await service.create_user(user_data, session)
    
    session.add.assert_called_once()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_duplicate_username():
    """
    create_user: raises ValidationError for duplicate username
    """
    service = UserService()
    service.get_user_by_username = AsyncMock(return_value=MagicMock())
    service.get_user_by_email = AsyncMock(return_value=None)
    
    session = MagicMock()
    user_data = UserCreate(
        username="existinguser",
        email="new@example.com",
        password="password",
        full_name="Test"
    )
    
    with pytest.raises(ValidationError, match="Username already exists"):
        await service.create_user(user_data, session)


@pytest.mark.asyncio
async def test_create_user_duplicate_email():
    """
    create_user: raises ValidationError for duplicate email
    """
    service = UserService()
    service.get_user_by_username = AsyncMock(return_value=None)
    service.get_user_by_email = AsyncMock(return_value=MagicMock())
    
    session = MagicMock()
    user_data = UserCreate(
        username="newuser",
        email="existing@example.com",
        password="password",
        full_name="Test"
    )
    
    with pytest.raises(ValidationError, match="Email already exists"):
        await service.create_user(user_data, session)


@pytest.mark.asyncio
async def test_authenticate_user_success():
    """
    authenticate_user: returns user for valid credentials
    """
    service = UserService()
    
    fake_user = MagicMock()
    fake_user.hashed_password = "hashed_pass"
    
    service.get_user_by_username = AsyncMock(return_value=fake_user)
    
    session = MagicMock()
    
    with patch('backend.services.user_service.verify_password', return_value=True):
        user = await service.authenticate_user("testuser", "password", session)
    
    assert user == fake_user


@pytest.mark.asyncio
async def test_authenticate_user_invalid_username():
    """
    authenticate_user: returns None for invalid username
    """
    service = UserService()
    service.get_user_by_username = AsyncMock(return_value=None)
    
    session = MagicMock()
    user = await service.authenticate_user("nonexistent", "password", session)
    
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password():
    """
    authenticate_user: returns None for invalid password
    """
    service = UserService()
    
    fake_user = MagicMock()
    fake_user.hashed_password = "hashed_pass"
    
    service.get_user_by_username = AsyncMock(return_value=fake_user)
    
    session = MagicMock()
    
    with patch('backend.services.user_service.verify_password', return_value=False):
        user = await service.authenticate_user("testuser", "wrongpassword", session)
    
    assert user is None


@pytest.mark.asyncio
async def test_create_access_token_for_user():
    """
    create_access_token_for_user: creates JWT token
    """
    service = UserService()
    
    fake_user = MagicMock()
    fake_user.id = 123
    fake_user.username = "testuser"
    
    with patch('backend.services.user_service.create_access_token', return_value="fake.jwt.token"):
        token = await service.create_access_token_for_user(fake_user)
    
    assert token == "fake.jwt.token"


@pytest.mark.asyncio
async def test_get_user_by_id_found():
    """
    get_user_by_id: returns user when found
    """
    service = UserService()
    session = MagicMock()
    
    fake_user = MagicMock(id=1, username="testuser")
    result = MagicMock()
    result.scalar_one_or_none.return_value = fake_user
    session.execute = AsyncMock(return_value=result)
    
    user = await service.get_user_by_id(1, session)
    
    assert user == fake_user


@pytest.mark.asyncio
async def test_get_user_by_username_found():
    """
    get_user_by_username: returns user when found
    """
    service = UserService()
    session = MagicMock()
    
    fake_user = MagicMock(username="testuser")
    result = MagicMock()
    result.scalar_one_or_none.return_value = fake_user
    session.execute = AsyncMock(return_value=result)
    
    user = await service.get_user_by_username("testuser", session)
    
    assert user == fake_user


@pytest.mark.asyncio
async def test_get_user_by_email_found():
    """
    get_user_by_email: returns user when found
    """
    service = UserService()
    session = MagicMock()
    
    fake_user = MagicMock(email="test@example.com")
    result = MagicMock()
    result.scalar_one_or_none.return_value = fake_user
    session.execute = AsyncMock(return_value=result)
    
    user = await service.get_user_by_email("test@example.com", session)
    
    assert user == fake_user
