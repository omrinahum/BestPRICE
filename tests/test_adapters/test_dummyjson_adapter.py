
from decimal import Decimal
import pytest
from backend.adapters.dummyjson_adapter import  dummyjson_to_offer

ITEMS = [
    {"id": 1, "title": "A", "price": 199.99, "rating": 4.7},
    {"id": 2, "title": "B", "price": 99.50,  "rating": 4.0},
    {"id": 3, "title": "C", "price": 49.90, "rating": 3.9},
    {"id": 4, "title": "D", "price": 999.0, "rating": 4.9},
]

def test_dummyjson_to_offer_basic():
    """dummyjson_to_offer: maps DummyJSON item into normalized OfferCreate dict."""
    item = {
        "id": "testID",
        "title": "testTitle",
        "price": 299.99,
        "thumbnail": "http://img/123.jpg",
        "rating": 4.5,
    }
    out = dummyjson_to_offer(item)
    
    # Check that everything maps correctly
    assert out["title"] == "testTitle"
    assert out["last_price"] == Decimal("299.99")
    assert out["currency"] == "USD"       # default currency for DummyJSON
    assert out["url"].endswith("/products/testID")
    assert out["source"] == "dummyjson"
    assert out["source_offer_id"] == "testID"
    assert out["seller"] is None          # DummyJSON has no seller info
    assert out["image_url"] == "http://img/123.jpg"
    assert isinstance(out["rating"], float)

def test_dummyjson_to_offer_missing_fields():
    """dummyjson_to_offer: handles missing optional fields gracefully."""
    item = {
        "id": "minimal",
        "title": "Minimal Product",
        "price": 50.00,
        # No thumbnail, rating
    }
    out = dummyjson_to_offer(item)
    
    assert out["title"] == "Minimal Product"
    assert out["last_price"] == Decimal("50.00")
    assert out["image_url"] is None
    # rating defaults to 0.0 when missing in dummyjson
    assert out["rating"] == 0.0


@pytest.mark.asyncio
async def test_search_dummyjson_http_error():
    """
    search_dummyjson: raises ExternalAPIError on HTTP errors
    """
    from unittest.mock import AsyncMock, patch, MagicMock
    from backend.utils.error import ExternalAPIError
    import httpx
    
    # Mock httpx to raise HTTP error
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404", request=MagicMock(), response=mock_response
    )
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        from backend.adapters.dummyjson_adapter import search_dummyjson
        
        with pytest.raises(ExternalAPIError, match="DummyJSON HTTP error"):
            await search_dummyjson("test")


@pytest.mark.asyncio
async def test_search_dummyjson_network_error():
    """
    search_dummyjson: raises ExternalAPIError on network failures
    """
    from unittest.mock import patch, AsyncMock
    from backend.utils.error import ExternalAPIError
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Network error")
        
        from backend.adapters.dummyjson_adapter import search_dummyjson
        
        with pytest.raises(ExternalAPIError, match="DummyJSON request failed"):
            await search_dummyjson("test")


@pytest.mark.asyncio
async def test_search_dummyjson_with_limit():
    """
    search_dummyjson: applies limit correctly
    """
    from unittest.mock import patch, AsyncMock, MagicMock
    
    mock_products = [{"id": i, "title": f"Product {i}", "price": 100} for i in range(20)]
    mock_response = MagicMock()
    mock_response.json.return_value = {"products": mock_products}
    mock_response.raise_for_status.return_value = None
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        from backend.adapters.dummyjson_adapter import search_dummyjson
        
        result = await search_dummyjson("test", limit=5)
        
        assert len(result["items_filtered"]) == 5

    """
    dummyjson_to_offer: handles missing optional fields correctly.
    """
    item = {
        "id": 1,
        "title": "missing fields",
        # price, thumbnail, rating missing
    }
    out = dummyjson_to_offer(item)
    assert out["title"] == "missing fields"
    assert out["last_price"] == 0     # Handles no price
    assert out["currency"] == "USD"   # Handles no currency
    assert out["url"] == "https://dummyjson.com/products/1"
    assert out["source"] == "dummyjson"
    assert out["source_offer_id"] == "1"
    assert out["seller"] is None      # Handles no seller and image- without crashing
    assert out["image_url"] is None
    assert out["rating"] == 0.0


