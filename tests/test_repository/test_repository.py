
from datetime import datetime, timedelta
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.repositories.repository import Repository
from backend.utils.error import ValidationError

def test_normalize_query_basic():
    """
    normalize_query: trims whitespace, deals with multiple spaces, and normalizes case.
    """
    s1 = Repository.normalize_query("  airpods   pro  2 ")
    s2 = Repository.normalize_query("airpods pro 2")
    
    # Check white spaces and multiple spaces trim
    assert s1.strip() == s1
    assert "  " not in s1
    # Check that both are normalized to the same
    assert s1 == s2

@pytest.mark.asyncio
async def test_get_recent_searches_limit_validation():
    """
    get_recent_searches: limit < 1 should raise ValidationError.
    """
    repo = Repository()
    session = MagicMock()  
    with pytest.raises(ValidationError):
        await repo.get_recent_searches(session, limit=0)


@pytest.mark.asyncio
async def test_get_cached_offers_expired(monkeypatch):
    """
    get_cached_offers: returns [] if cache is expired.
    """
    repo = Repository()
    session = MagicMock()

    # Mock everything needed for DB simulation
    old_search = MagicMock(created_at=datetime.utcnow() - timedelta(minutes=120))
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = old_search

    # Fake database response
    monkeypatch.setattr(session, "execute", AsyncMock(return_value=mock_execute_result))

    result = await repo.get_cached_offers("test", 60, session)
    assert result == []

@pytest.mark.asyncio
async def test_get_cached_offers_valid(monkeypatch):
    """
    get_cached_offers: returns search if cache is valid.
    """
    repo = Repository()
    session = MagicMock()

    # Mock everything needed for DB simulation
    valid_search = MagicMock(created_at=datetime.utcnow())
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = valid_search

    # Fake database response
    monkeypatch.setattr(session, "execute", AsyncMock(return_value=mock_execute_result))

    result = await repo.get_cached_offers("test", 60, session)
    assert result == valid_search

