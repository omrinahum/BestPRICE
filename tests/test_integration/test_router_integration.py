import pytest
from httpx import AsyncClient
from backend.main import app


@pytest.mark.asyncio
async def test_auth_register_login_flow():
    """
    Test complete auth flow: register -> login -> get token
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register user
        unique_id = id(client)
        register_data = {
            "username": f"routertest_{unique_id}",
            "email": f"routertest_{unique_id}@example.com",
            "password": "TestPass123",
            "full_name": "Router Test User"
        }
        reg_resp = await client.post("/auth/register", json=register_data)
        assert reg_resp.status_code == 200
        
        # Login
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"]
        }
        login_resp = await client.post("/auth/login", json=login_data)
        assert login_resp.status_code == 200
        token_data = login_resp.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_auth_duplicate_registration():
    """
    Test that duplicate registration fails appropriately
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        unique_id = id(client)
        user_data = {
            "username": f"duplicate_{unique_id}",
            "email": f"duplicate_{unique_id}@example.com",
            "password": "Pass123",
            "full_name": "Duplicate User"
        }
        
        # First registration
        resp1 = await client.post("/auth/register", json=user_data)
        assert resp1.status_code == 200
        
        # Second registration with same username should fail with 422 (validation error)
        resp2 = await client.post("/auth/register", json=user_data)
        assert resp2.status_code == 422


@pytest.mark.asyncio
async def test_auth_invalid_login():
    """
    Test login with invalid credentials
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_data = {
            "username": "nonexistentuser",
            "password": "wrongpassword"
        }
        resp = await client.post("/auth/login", json=login_data)
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_offers_pagination():
    """
    Test offers endpoint pagination validation
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Invalid page number
        resp = await client.get("/offers/?search_id=1&page=0&page_size=10")
        assert resp.status_code == 422
        
        # Invalid page size
        resp = await client.get("/offers/?search_id=1&page=1&page_size=0")
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_offers_price_history():
    """
    Test price history endpoint for non-existent offer
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/offers/price/999999")
        assert resp.status_code == 200
        assert resp.json() == []


@pytest.mark.asyncio
async def test_search_recent():
    """
    Test recent searches endpoint
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/search/recent?limit=5")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_deals_endpoint():
    """
    Test deals endpoint returns valid structure
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/deals/recent")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
