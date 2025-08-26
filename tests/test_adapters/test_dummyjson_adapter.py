
from decimal import Decimal
import pytest
from backend.adapters.dummyjson_adapter import apply_client_side_filters, dummyjson_to_offer

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


def test_price_range_filter():
    """
    Test the price range filter.
    """
    filtered = apply_client_side_filters(ITEMS, {"price": [90, 200]})
    ids = [item["id"] for item in filtered]
    assert set(ids) == {1, 2}

def test_no_price_filter():
    filtered = apply_client_side_filters(ITEMS, {})
    assert filtered == ITEMS

def test_empty_items():
    filtered = apply_client_side_filters([], {"price": [0, 1000]})
    assert filtered == []

def test_price_filter_out_of_range():
    filtered = apply_client_side_filters(ITEMS, {"price": [2000, 3000]})
    assert filtered == []
