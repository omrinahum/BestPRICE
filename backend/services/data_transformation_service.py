# backend/services/data_transformation_service.py
"""
Service Layer - Handles data transformation and normalization
"""
from typing import List, Dict
from backend.adapters.ebay_adapter import ebay_to_offer
from backend.adapters.dummyjson_adapter import dummyjson_to_offer
from backend.adapters.amazon_adapter import amazon_to_offer

def transform_search_results(raw_results: Dict[str, List[dict]]) -> List[dict]:
    """
    Transform raw API results into normalized offer data
     """
    all_offers = []
    # Transform eBay results
    for item in raw_results.get('ebay', []):
        try:
            offer_data = ebay_to_offer(item)
            all_offers.append(offer_data)
        except Exception as e:
            print(f"Error transforming eBay item {item.get('itemId', 'unknown')}: {e}")

    # Transform DummyJSON results
    for item in raw_results.get('dummyjson', {}).get('items_filtered', []):
        try:
            offer_data = dummyjson_to_offer(item)
            all_offers.append(offer_data)
        except Exception as e:
            print(f"Error transforming DummyJSON item {item.get('id', 'unknown')}: {e}")

     # Amazon
    for item in raw_results.get('amazon', {}).get('products', []):
        try:
            offer_data = amazon_to_offer(item)
            all_offers.append(offer_data)
        except Exception as e:
            print(f"Error transforming Amazon item {item.get('asin', 'unknown')}: {e}")

    return all_offers