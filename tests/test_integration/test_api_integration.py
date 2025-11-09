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
    Test creating a search and getting recent searches (without auth).
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a search with a dummy auth header
        payload = {"query": "iphone"}
        headers = {"Authorization": "Bearer dummy_token_for_optional_auth"}
        res = await client.post("/search/", json=payload, headers=headers)

        # The search should still be created successfully
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
    Test offers and their price history (with dummy auth).
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a search with dummy auth header
        payload = {"query": "laptop"}
        headers = {"Authorization": "Bearer dummy_token_for_optional_auth"}
        resp = await client.post("/search/", json=payload, headers=headers)

        assert resp.status_code == 200
        search_id = resp.json()["id"]

        # Get offers for the search
        offers_resp = await client.get(f"/offers/?search_id={search_id}&page=1&page_size=10")

        # Check response status and type
        assert offers_resp.status_code == 200
        offers_data = offers_resp.json()
        assert isinstance(offers_data, dict)
        assert "offers" in offers_data
        
        # If there are offers, check price history for the first one
        if offers_data["offers"]:
            offer_id = offers_data["offers"][0]["id"]
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
        response_data = offers_resp.json()
        assert "offers" in response_data
        assert response_data["offers"] == []

        # Not found offer_id for price history - should return 200 with empty list
        price_resp = await client.get("/offers/price/999999")
        assert price_resp.status_code == 200
        assert price_resp.json() == []

@pytest.mark.asyncio
async def test_search_with_price_filters():
    """
    Test creating a search and filtering offers by price range (with dummy auth).
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create a search with dummy auth header
        data = {"query": "iphone"}
        headers = {"Authorization": "Bearer dummy_token_for_optional_auth"}
        res = await client.post("/search/", json=data, headers=headers)
        
        # Check response
        assert res.status_code == 200
        response_data = res.json()
        assert "id" in response_data and response_data["query"] == "iphone"
        search_id = response_data["id"]

        # Get offers for the search with price filters
        offers_resp = await client.get(f"/offers/?search_id={search_id}&page=1&page_size=10&min_price=100&max_price=300")
        assert offers_resp.status_code == 200
        offers_data = offers_resp.json()
        
        # Check structure
        assert isinstance(offers_data, dict)
        assert "offers" in offers_data
        
        # If offers exist, check they're in the price range
        if offers_data["offers"]:
            for offer in offers_data["offers"]:
                if "last_price" in offer and offer["last_price"]:
                    assert 100 <= float(offer["last_price"]) <= 300


@pytest.mark.asyncio
async def test_end_to_end_user_auth_flow():
    """
    End-to-end test: register -> login -> create authenticated search
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Step 1: Register a new user
        register_data = {
            "username": f"testuser_{id(client)}",
            "email": f"test_{id(client)}@example.com",
            "password": "SecurePass123",
            "full_name": "Test User"
        }
        register_resp = await client.post("/auth/register", json=register_data)
        assert register_resp.status_code == 200
        user_data = register_resp.json()
        assert "id" in user_data
        assert user_data["username"] == register_data["username"]
        
        # Step 2: Login to get access token
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"]
        }
        login_resp = await client.post("/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token_data = login_resp.json()
        assert "access_token" in token_data
        access_token = token_data["access_token"]
        
        # Step 3: Use token to create authenticated search
        headers = {"Authorization": f"Bearer {access_token}"}
        search_payload = {"query": "authenticated search test"}
        search_resp = await client.post("/search/", json=search_payload, headers=headers)
        assert search_resp.status_code == 200
        search_data = search_resp.json()
        assert search_data["query"] == "authenticated search test"
        assert "id" in search_data
        
        # Verified: User can register, login, and create authenticated searches successfully
