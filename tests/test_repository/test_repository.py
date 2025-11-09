
from datetime import datetime, timedelta
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.repositories.repository import Repository
from backend.utils.error import ValidationError

def test_normalize_query_basic():
    """
    normalize_query: trims whitespace, deals with multiple spaces, and normalizes case.
    """
    # Test normalization with messy input
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
    
    # Attempt to get searches with invalid limit
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
    # Create an old search from 2 hours ago
    old_search = MagicMock(created_at=datetime.utcnow() - timedelta(minutes=120))
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = old_search

    # Fake database response
    monkeypatch.setattr(session, "execute", AsyncMock(return_value=mock_execute_result))

    # Try to get cached offers with 60 minute max age (should be expired)
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
    # Create a recent search (just created now)
    valid_search = MagicMock(created_at=datetime.utcnow())
    mock_execute_result = MagicMock()
    mock_execute_result.scalar_one_or_none.return_value = valid_search

    # Fake database response
    monkeypatch.setattr(session, "execute", AsyncMock(return_value=mock_execute_result))

    # Try to get cached offers with 60 minute max age (should be valid)
    result = await repo.get_cached_offers("test", 60, session)
    assert result == valid_search


# Additional comprehensive tests for better coverage

@pytest.mark.asyncio
async def test_normalize_query_validation():
    """
    normalize_query: raises ValidationError for invalid input
    """
    # Empty string should fail
    with pytest.raises(ValidationError, match="Query must be a non-empty string"):
        Repository.normalize_query("")
    # None should fail
    with pytest.raises(ValidationError):
        Repository.normalize_query(None)


@pytest.mark.asyncio
async def test_create_search_with_user():
    """
    create_search: creates search with user_id
    """
    from backend.schemas.search_schema import SearchCreate
    repo = Repository()
    session = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    
    # Create search associated with a user
    search_data = SearchCreate(query="iPhone 15")
    await repo.create_search(search_data, session, user_id=123)
    
    # Verify search was added to session
    session.add.assert_called_once()
    added_search = session.add.call_args[0][0]
    assert added_search.query == "iPhone 15"
    assert added_search.normalized_query == "iphone 15"
    assert added_search.user_id == 123


@pytest.mark.asyncio
async def test_get_or_create_offer_existing():
    """
    get_or_create_offer: updates existing offer
    """
    repo = Repository()
    session = MagicMock()
    
    # Mock an existing offer in the database
    existing_offer = MagicMock()
    existing_offer.last_price = 100.00
    existing_offer.rating = 4.0
    
    result = MagicMock()
    result.scalar_one_or_none.return_value = existing_offer
    session.execute = AsyncMock(return_value=result)
    session.flush = AsyncMock()
    
    # Try to create/update with new data
    data = {
        "source": "ebay",
        "source_offer_id": "123",
        "last_price": 89.99,
        "rating": 4.5,
        "title": "Test Product"
    }
    
    offer = await repo.get_or_create_offer(data, session)
    
    # Verify the existing offer was updated (not created new)
    assert offer == existing_offer
    assert offer.last_price == 89.99
    assert offer.rating == 4.5
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_or_create_offer_new():
    """
    get_or_create_offer: creates new offer when not found
    """
    repo = Repository()
    session = MagicMock()
    
    # Mock no existing offer in database
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)
    session.flush = AsyncMock()
    
    # Try to create new offer
    data = {
        "source": "amazon",
        "source_offer_id": "B08N5WRWNW",
        "title": "New Product",
        "last_price": 199.99,
        "currency": "USD",
        "url": "https://amazon.com/test",
        "seller": "Amazon",
        "image_url": "https://image.url",
        "rating": 4.8
    }
    
    await repo.get_or_create_offer(data, session)
    
    # Verify a new offer was added
    session.add.assert_called_once()
    added_offer = session.add.call_args[0][0]
    assert added_offer.title == "New Product"
    assert added_offer.last_price == 199.99


@pytest.mark.asyncio
async def test_create_search_offer_link():
    """
    create_search_offer_link: creates link object
    """
    repo = Repository()
    link = repo.create_search_offer_link(search_id=5, offer_id=10)
    
    assert link.search_id == 5
    assert link.offer_id == 10


@pytest.mark.asyncio
async def test_create_price_history():
    """
    create_price_history: creates price history object
    """
    repo = Repository()
    history = repo.create_price_history(offer_id=7, price=49.99, currency="USD")
    
    assert history.offer_id == 7
    assert history.price == 49.99
    assert history.currency == "USD"


@pytest.mark.asyncio
async def test_update_or_create_offer_with_history():
    """
    update_or_create_offer_with_history: processes multiple offers
    """
    repo = Repository()
    # Mock the get_or_create_offer method to return fake offers
    repo.get_or_create_offer = AsyncMock(side_effect=[
        MagicMock(id=1, last_price=100, currency="USD"),
        MagicMock(id=2, last_price=200, currency="USD")
    ])
    
    session = MagicMock()
    session.commit = AsyncMock()
    
    # Process two offers
    offers_data = [
        {"source": "ebay", "source_offer_id": "1", "last_price": 100, "title": "Offer1", "url": "http://1", "currency": "USD"},
        {"source": "amazon", "source_offer_id": "2", "last_price": 200, "title": "Offer2", "url": "http://2", "currency": "USD"}
    ]
    
    result = await repo.update_or_create_offer_with_history(offers_data, search_id=99, session=session)
    
    # Verify all offers were processed
    assert len(result) == 2
    assert session.add_all.call_count == 2  # Should add links and price histories
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_recent_searches_success():
    """
    get_recent_searches: returns list of searches
    """
    repo = Repository()
    session = MagicMock()
    
    # Mock database returning two searches
    fake_searches = [
        MagicMock(id=1, query="phone"),
        MagicMock(id=2, query="laptop")
    ]
    
    result = MagicMock()
    result.scalars().all.return_value = fake_searches
    session.execute = AsyncMock(return_value=result)
    
    searches = await repo.get_recent_searches(session, limit=10)
    
    # Verify we got the correct searches back
    assert len(searches) == 2


@pytest.mark.asyncio
async def test_get_user_recent_searches_success():
    """
    get_user_recent_searches: returns user-specific searches
    """
    repo = Repository()
    session = MagicMock()
    
    # Mock database returning searches for a specific user
    fake_searches = [MagicMock(id=1, query="phone", user_id=42)]
    
    result = MagicMock()
    result.scalars().all.return_value = fake_searches
    session.execute = AsyncMock(return_value=result)
    
    # Get searches for user 42
    searches = await repo.get_user_recent_searches(user_id=42, session=session, limit=10)
    
    # Verify we got user-specific searches
    assert len(searches) == 1


@pytest.mark.asyncio
async def test_get_user_recent_searches_validation():
    """
    get_user_recent_searches: validates limit parameter
    """
    repo = Repository()
    session = MagicMock()
    
    # Attempt to get searches with invalid limit
    with pytest.raises(ValidationError):
        await repo.get_user_recent_searches(user_id=1, session=session, limit=0)


@pytest.mark.asyncio
async def test_get_cached_offers_not_found(monkeypatch):
    """
    get_cached_offers: returns empty list when no cache found
    """
    repo = Repository()
    session = MagicMock()
    
    # Mock database returning no cached search
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    monkeypatch.setattr(session, "execute", AsyncMock(return_value=result))
    
    # Try to get cache for a query that doesn't exist
    cached = await repo.get_cached_offers("newquery", max_age_minutes=10, session=session)
    
    # Should return empty list when no cache found
    assert cached == []
