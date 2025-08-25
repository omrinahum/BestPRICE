import logging
from typing import Optional, Dict, Any, List

import httpx

from backend.utils.price import to_decimal, normalize_currency
from backend.utils.error import ExternalAPIError

# DummyJSON base URL for product search
DUMMYJSON_BASE_URL = "https://dummyjson.com/products/search"

def _apply_client_side_filters(items: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Apply client-side filters to the list of items, because DummyJSON does not support server-side filtering.
    """
    if not items:
        return items

    # price range filter 
    price_rng = filters.get("price")
    if price_rng and len(price_rng) == 2:
        minp = float(price_rng[0] or 0)
        maxp = float(price_rng[1] or float("inf"))
        filtered_items = []
        for item in items:
            price = float(item.get("price", 0))
            if minp <= price <= maxp:
                filtered_items.append(item)
        items = filtered_items

    # condition is not supported by DummyJSON so ignore
    return items


async def search_dummyjson(query: str, filters: Dict[str, Any], limit: int = 50) -> Dict[str, Any]:
    """
    Execute a search query on DummyJSON.
    We'll apply price-range filtering client-side after fetching.
    """
    # Build URL
    url = f"{DUMMYJSON_BASE_URL}?q={query}"

    try:
        # Fetch data from DummyJSON
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        logging.error(f"[DummyJSON] HTTP error: {e.response.status_code} {e.response.text}")
        raise ExternalAPIError(f"DummyJSON HTTP error: {e.response.status_code}") from e
    except Exception as e:
        logging.error(f"[DummyJSON] request failed: {e}")
        raise ExternalAPIError("DummyJSON request failed") from e

    # Ensure structure, and apply filters
    products = data.get("products", [])
    products = _apply_client_side_filters(products, filters)

    # Apply limit (rounded)
    if limit:
        rounded_limit = round(limit)
        if rounded_limit > 0:
            products = products[:rounded_limit]
    
    data["items_filtered"] = products
    logging.info(f"[DummyJSON] fetched {len(products)} items (after filters) for query='{query}'")
    return data


def dummyjson_to_offer(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a DummyJSON product to an OfferCreate dict, based on the json format of DummyJSON.
    """
    return {
        "title": item.get("title", "") or "",
        "last_price": to_decimal(item.get("price", 0) or 0),
        "currency": normalize_currency("USD"), # Default currency, not provided by DummyJSON
        "url": f"https://dummyjson.com/products/{item.get('id')}",
        "source": "dummyjson",
        "source_offer_id": str(item.get("id", "")),
        "seller": None,  # no seller field in DummyJSON
        "image_url": item.get("thumbnail"),
        "rating": float(item.get("rating", 0) or 0),
    }
