import logging
from typing import Optional, Dict, Any, List

import httpx

from backend.utils.price import to_decimal, normalize_currency
from backend.utils.error import ExternalAPIError

# DummyJSON base URL for product search
DUMMYJSON_BASE_URL = "https://dummyjson.com/products/search"

async def search_dummyjson(query: str, limit: int = 120) -> Dict[str, Any]:
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

    products = data.get("products", [])

    # Apply limit (rounded)
    if limit:
        rounded_limit = round(limit)
        if rounded_limit > 0:
            products = products[:rounded_limit]
    
    data["items_filtered"] = products
    logging.info(f"[DummyJSON] fetched {len(products)} items for query='{query}'")
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
