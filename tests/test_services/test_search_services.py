import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from backend.services.search_services import SearchService
from backend.schemas.search_schema import SearchCreate
from backend.utils.error import ExternalAPIError, NotFoundError




def make_search_obj(id=1, query="laptop", normalized_query="laptop", created_at=None):
    """
    Helper function to create a simple object compatible with SearchResponse.
    """
    return SimpleNamespace(
        id=id,
        query=query,
        normalized_query=normalized_query,
        created_at=created_at or datetime.utcnow()
    )

@pytest.mark.asyncio
async def test_search_all_sources_success(monkeypatch):
    """
    search_all_sources: returns aggregated results when both adapters succeed.
    """
    # Fake adapter functions return unfiltered results
    async def fake_search_ebay(q, limit=50, token=None):
        return {"itemSummaries": [{"itemId": "E1"}, {"itemId": "E2"}]}
    async def fake_search_dummyjson(q, limit=50):
        return {"products": [{"id": 10}, {"id": 11}]}

    # Switch api functions with the fake ones
    monkeypatch.setattr("backend.services.search_services.search_ebay", fake_search_ebay)
    monkeypatch.setattr("backend.services.search_services.search_dummyjson", fake_search_dummyjson)

    service = SearchService(repository=MagicMock(), transform_service=MagicMock())

    res = await service.search_all_sources("test")

    # After filtering, the results should be the same as the input (since no filter matches)
    assert "ebay" in res and "dummyjson" in res
    assert res["ebay"] == [{"itemId": "E1"}, {"itemId": "E2"}]
    assert res["dummyjson"]["items_filtered"] == [{"id": 10}, {"id": 11}]

@pytest.mark.asyncio
async def test_search_all_sources_ebay_error(monkeypatch):
    """
    search_all_sources: raises ExternalAPIError when eBay adapter fails.
    """
    # Fake adapter functions
    async def bad_ebay(q):
        raise RuntimeError("ebay down")
    async def ok_dummy(q):
        return {"items_filtered": []}

    # Switch api functions with the fake ones
    monkeypatch.setattr("backend.services.search_services.search_ebay", bad_ebay)
    monkeypatch.setattr("backend.services.search_services.search_dummyjson", ok_dummy)

    service = SearchService(repository=MagicMock(), transform_service=MagicMock())

    # Check that ExternalAPIError is raised
    with pytest.raises(ExternalAPIError):
        await service.search_all_sources("x")

@pytest.mark.asyncio
async def test_search_all_sources_dummyjson_error(monkeypatch):
    """search_all_sources: raises ExternalAPIError when DummyJSON adapter fails."""
    # Fake adapter functions
    async def ok_ebay(q):
        return {"itemSummaries": []}
    async def bad_dummy(q):
        raise ValueError("dummyjson broken")

    # Switch api functions with the fake ones
    monkeypatch.setattr("backend.services.search_services.search_ebay", ok_ebay)
    monkeypatch.setattr("backend.services.search_services.search_dummyjson", bad_dummy)

    service = SearchService(repository=MagicMock(), transform_service=MagicMock())

    # Check that ExternalAPIError is raised
    with pytest.raises(ExternalAPIError):
        await service.search_all_sources("x")


@pytest.mark.asyncio
async def test_perform_search_cache_hit():
    """
    perform_search: returns cached SearchResponse when cache exists (no external calls).
    """
    repo = MagicMock()
    # Simulate a successful normalization
    repo.normalize_query.return_value = "laptop"
    # Simulate a found cached search record
    cached = make_search_obj(id=99, normalized_query="laptop")
    repo.get_cached_offers = AsyncMock(return_value=cached)

    # Ensure that if cache is hit, no create/search/transform/update are called
    repo.create_search = AsyncMock()
    repo.update_or_create_offer_with_history = AsyncMock()

    service = SearchService(repository=repo, transform_service=MagicMock())

    search_data = SearchCreate(query="laptop")
    session = MagicMock()

    res = await service.perform_search(search_data, session)

    # Check that the correct cached result is returned
    assert res.id == 99
    # Check that only cached methods were called
    repo.get_cached_offers.assert_awaited_once()
    repo.create_search.assert_not_called()
    repo.transform_service.assert_not_called()
    repo.update_or_create_offer_with_history.assert_not_called()

@pytest.mark.asyncio
async def test_perform_search_cache_miss():
    """
    perform_search: creates search, fetches sources, transforms, stores, returns SearchResponse.
    """
    repo = MagicMock()
    repo.normalize_query.return_value = "phone"
    repo.get_cached_offers = AsyncMock(return_value=None)

    # The repository returns a new created search 
    created = make_search_obj(id=1, query="phone", normalized_query="phone")
    repo.create_search = AsyncMock(return_value=created)
    repo.update_or_create_offer_with_history = AsyncMock()

    # Faking ebay and dummy json responses
    fake_raw = {"ebay": [{"itemId": "E1"}], "dummyjson": {"items_filtered": [{"id": 7}] }}

    service = SearchService(repository=repo, transform_service=MagicMock(return_value=[{"title": "ok"}]))
    service.search_all_sources = AsyncMock(return_value=fake_raw)

    search_data = SearchCreate(query="phone")
    session = MagicMock()

    res = await service.perform_search(search_data, session)

    # Validate overall flow of a cache miss in perform_search 
    assert res.id == 1
    service.search_all_sources.assert_awaited_once_with("phone")
    service.transform_service.assert_called_once_with(fake_raw)
    repo.update_or_create_offer_with_history.assert_awaited_once()
    repo.create_search.assert_awaited_once_with(search_data, session)

@pytest.mark.asyncio
async def test_get_recent_searches_found():
    """
    get_recent_searches: returns list of SearchResponse when repository returns results.
    """
    repo = MagicMock()
    # Create two fake Searches
    s1 = make_search_obj(id=1, query="q1", normalized_query="q1")
    s2 = make_search_obj(id=2, query="q2", normalized_query="q2")
    repo.get_recent_searches = AsyncMock(return_value=[s1, s2])

    service = SearchService(repository=repo, transform_service=MagicMock())
    session = MagicMock()

    res = await service.get_recent_searches(session, limit=2)

    # Check that the correct result is returned
    assert [r.id for r in res] == [1, 2]
    repo.get_recent_searches.assert_awaited_once_with(session, 2)

@pytest.mark.asyncio
async def test_get_recent_searches_empty():
    """
    get_recent_searches: returns an empty list when no searches are found.
    """
    repo = MagicMock()
    repo.get_recent_searches = AsyncMock(return_value=[])
    service = SearchService(repository=repo, transform_service=MagicMock())
    session = MagicMock()

    history = await service.get_recent_searches(session, limit=5)
    assert history == []
