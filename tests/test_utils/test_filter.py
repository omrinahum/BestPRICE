import pytest
from backend.utils.filter import apply_filters

def test_apply_filters_price():
    """
    Test price filtering.
    """
    # Generate fake items
    items = [
        {"last_price": 50},
        {"last_price": 150},
        {"last_price": 500},
        {"last_price": 1200},
    ]
    filters = {"price": [100, 1000]}
    filtered = apply_filters(items, filters)
    assert [item["last_price"] for item in filtered] == [150, 500]

def test_apply_filters_no_price():
    """
    Test filtering without price range.
    """
    # Generate fake items
    items = [
        {"last_price": 50},
        {"last_price": 150},
    ]
    filters = {}
    filtered = apply_filters(items, filters)
    assert filtered == items

def test_apply_filters_empty_items():
    """
    Test filtering with empty item list.
    """
    items = []
    filters = {"price": [0, 1000]}
    filtered = apply_filters(items, filters)
    assert filtered == []

def test_apply_filters_price_out_of_range():
    """
    Test filtering with price range out of bounds.
    """
    items = [
        {"last_price": 50},
        {"last_price": 150},
    ]
    filters = {"price": [200, 300]}
    filtered = apply_filters(items, filters)
    assert filtered == []

