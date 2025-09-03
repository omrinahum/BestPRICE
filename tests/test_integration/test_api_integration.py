import pytest
from httpx import AsyncClient
from backend.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_search_create_and_recent():
    """
    Test creating a search and getting recent searches.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a search
        payload = {"query": "iphone"}
        res = await client.post("/search/", json=payload)

        # Check response
        assert res.status_code == 200
        data = res.json()
        assert "id" in data and data["query"] == "iphone"
        search_id = data["id"]

        # Check that the recent searches include the new search
        recent = await client.get("/search/recent?limit=5")
        assert recent.status_code == 200
        recent_list = recent.json()
        assert any(s["id"] == search_id for s in recent_list)

@pytest.mark.asyncio
async def test_offers_and_price_history():
    """
    Test offers and their price history.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a search
        payload = {"query": "laptop"}
        resp = await client.post("/search/", json=payload)

        assert resp.status_code == 200
        search_id = resp.json()["id"]

        # Get offers for the search
        offers_resp = await client.get(f"/offers/?search_id={search_id}&page=1&page_size=10")

        # Check response status and type
        assert offers_resp.status_code == 200
        offers = offers_resp.json()
        assert isinstance(offers, list)
        
        # If there are offers, check price history for the first one
        if offers:
            offer_id = offers[0]["id"]
            price_resp = await client.get(f"/offers/price/{offer_id}")

            # Check response status and type
            assert price_resp.status_code == 200
            price_history = price_resp.json()
            assert isinstance(price_history, list)

@pytest.mark.asyncio
async def test_error_handling():
    """
    Test error handling for offers endpoint.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Invalid pagination - should return 422
        offers_resp = await client.get("/offers/?search_id=1&page=0&page_size=10")
        assert offers_resp.status_code == 422
        assert "detail" in offers_resp.json()

        # Not found search_id - should return 200 with empty list
        offers_resp = await client.get("/offers/?search_id=999999&page=1&page_size=10")
        assert offers_resp.status_code == 200
        assert offers_resp.json() == []

        # Not found offer_id for price history - should return 200 with empty list
        price_resp = await client.get("/offers/price/999999")
        assert price_resp.status_code == 200
        assert price_resp.json() == []

@pytest.mark.asyncio
async def test_search_with_price_filters():
    """
    Test creating a search and filtering offers by price range.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a search
        data = {"query": "iphone"}
        res = await client.post("/search/", json=data)
        
        # Check response
        assert res.status_code == 200
        data = res.json()
        assert "id" in data and data["query"] == "iphone"
        search_id = data["id"]

        # Get offers for the search with price filters
        offers_resp = await client.get(f"/offers/?search_id={search_id}&page=1&page_size=10&min_price=100&max_price=300")
        assert offers_resp.status_code == 200
        offers = offers_resp.json()
        
        # If offers exist, check they're in the price range
        if isinstance(offers, list) and offers:
            for offer in offers:
                if "last_price" in offer and offer["last_price"]:
                    assert 100 <= float(offer["last_price"]) <= 300