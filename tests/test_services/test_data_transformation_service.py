
import pytest
from unittest.mock import MagicMock
from backend.services.data_transformation_service import transform_search_results

def test_transform_search_results_aggregates(monkeypatch):
    """
    transform_search_results: aggregates outputs from ebay_to_offer and dummyjson_to_offer.
    """
    # Fake raw items
    raw = {
        "ebay": [{"itemId": "E1"}, {"itemId": "E2"}],
        "dummyjson": {"items_filtered": [{"id": 10}, {"id": 11}]}
    }

    # Patch converters to return normalized dicts
    monkeypatch.setattr("backend.services.data_transformation_service.ebay_to_offer",
                        lambda item: {"src": "ebay", "id": item["itemId"]})
    monkeypatch.setattr("backend.services.data_transformation_service.dummyjson_to_offer",
                        lambda item: {"src": "dummyjson", "id": item["id"]})

    result = transform_search_results(raw)

    # Assert
    assert result == [
        {"src": "ebay", "id": "E1"},
        {"src": "ebay", "id": "E2"},
        {"src": "dummyjson", "id": 10},
        {"src": "dummyjson", "id": 11},
    ]

def test_transform_search_results_handles_bad_items(monkeypatch):
    """
    transform_search_results: continues when a converter raises an exception.
    """
    # Fake raw items
    raw = {
        "ebay": [{"itemId": "OK"}, {"itemId": "BAD"}],
        "dummyjson": {"items_filtered": [{"id": 1}, {"id": 2}]}
    }

    # Fake ebay_to_offer converter
    def ebay_conv(item):
        if item["itemId"] == "BAD":
            raise ValueError("boom")
        return {"src": "ebay", "id": item["itemId"]}
    # Fake dummyjson_to_offer converter
    def dummy_conv(item):
        return {"src": "dummyjson", "id": item["id"]}

    monkeypatch.setattr("backend.services.data_transformation_service.ebay_to_offer", ebay_conv)
    monkeypatch.setattr("backend.services.data_transformation_service.dummyjson_to_offer", dummy_conv)

    result = transform_search_results(raw)
    # The bad item is skipped, others included
    assert result == [
        {"src": "ebay", "id": "OK"},
        {"src": "dummyjson", "id": 1},
        {"src": "dummyjson", "id": 2},
    ]
