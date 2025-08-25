
import pytest
from backend.adapters.ebay_adapter import ebay_to_offer, convert_conditions_for_ebay

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

def test_convert_conditions_for_ebay_known_values():
    """
    convert_conditions_for_ebay: converts known readable conditions to eBay IDs.
    """
    # Known conditions mapping
    out = convert_conditions_for_ebay(["new", "refurbished", "used", "not_in_map"])

    # Check that known conditions are converted correctly
    assert out == [1000, 2000, 3000]
    # Unknown entries should be ignored 
    assert "not_in_map" not in out

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