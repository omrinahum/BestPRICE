
import pytest
from backend.adapters.ebay_adapter import ebay_to_offer

def test_ebay_to_offer_basic():
    """
    ebay_to_offer: maps eBay item into normalized OfferCreate dict.
    """
    # Fake eBay item
    item = {
        "itemId": "testID",
        "title": "testTitle",
        "price": {"value": "100.00", "currency": "USD"},
        "itemWebUrl": "https://www.ebay.com/itm/testID",
        "seller": {"username": "testSeller", "feedbackPercentage": 95.0},
        "image": {"imageUrl": "https://i.ebayimg.com/images/testID"},
    }

    out = ebay_to_offer(item)

    # Check that everything maps correctly
    assert out["title"] == "testTitle"
    assert str(out["last_price"]) in ("100.00", "100.0")
    assert out["currency"] == "USD"
    assert out["url"] == "https://www.ebay.com/itm/testID"
    assert out["source"] == "ebay"
    assert out["source_offer_id"] == "testID"
    assert out["seller"] == "testSeller"
    assert out["image_url"] == "https://i.ebayimg.com/images/testID"
    assert isinstance(out["rating"], float)

def test_ebay_to_offer_missing_fields():
    """
    ebay_to_offer: handles missing optional fields correctly.
    """
    item = {
        "itemId": "testID",
        "title": "testTitle",
        # price, seller, image and more missing
    }
    out = ebay_to_offer(item)
    assert out["title"] == "testTitle"
    assert out["last_price"] == 0
    assert out["currency"] == "USD"
    assert out["seller"] is None
    assert out["image_url"] is None
    assert out["rating"] is None


@pytest.mark.asyncio
async def test_search_ebay_http_error():
    """
    search_ebay: handles HTTP errors gracefully
    """
    from unittest.mock import AsyncMock, patch, MagicMock
    from backend.utils.error import ExternalAPIError
    import httpx
    
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500", request=MagicMock(), response=mock_response
    )
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        from backend.adapters.ebay_adapter import search_ebay
        
        with pytest.raises(ExternalAPIError, match="eBay API HTTP error"):
            await search_ebay("test", token="fake_token")


@pytest.mark.asyncio
async def test_search_ebay_with_filters():
    """
    search_ebay: returns valid structure
    """
    from unittest.mock import patch, AsyncMock, MagicMock
    
    mock_items = [
        {"itemId": "1", "title": "Product 1", "price": {"value": "50", "currency": "USD"}},
        {"itemId": "2", "title": "Product 2", "price": {"value": "150", "currency": "USD"}}
    ]
    mock_response = MagicMock()
    mock_response.json.return_value = {"itemSummaries": mock_items}
    mock_response.raise_for_status.return_value = None
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        from backend.adapters.ebay_adapter import search_ebay
        
        result = await search_ebay("test", token="fake_token")
        
        assert "itemSummaries" in result


@pytest.mark.asyncio  
async def test_search_ebay_no_token():
    """
    search_ebay: handles missing token by fetching one
    """
    from unittest.mock import patch, AsyncMock, MagicMock
    from backend.adapters.ebay_adapter import search_ebay
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"itemSummaries": []}
    mock_response.raise_for_status.return_value = None
    
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    
    with patch('httpx.AsyncClient', return_value=mock_client):
        with patch('backend.adapters.ebay_adapter.get_valid_ebay_token', return_value="auto_token"):
            result = await search_ebay("test", token=None)
            
            # Verify it returns a valid structure
            assert isinstance(result, dict)
            assert "itemSummaries" in result
