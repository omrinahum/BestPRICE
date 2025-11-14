import logging
import os
from typing import Dict, Any, Optional
import httpx
from backend.utils.price import to_decimal, normalize_currency
from backend.utils.error import ExternalAPIError

AMAZON_BASE_URL = "https://real-time-amazon-data.p.rapidapi.com/search"
AMAZON_API_KEY = os.getenv("AMAZON_API_KEY")
AMAZON_API_HOST = "real-time-amazon-data.p.rapidapi.com"



async def search_amazon(query: str, limit: int = 120) -> Dict[str, Any]:
    """
    Execute a search query on Amazon via RapidAPI.
    Only uses the 'query' parameter.
    """

    # Set up query parameters
    params = {
        "query": query,
        "page": 1,
        "country": "US",
        "sort_by": "RELEVANCE",
        "product_condition": "ALL",
        "is_prime": "false",
        "deals_and_discounts": "NONE"
    }

    # Set up headers
    headers = {
        "x-rapidapi-key": AMAZON_API_KEY,
        "x-rapidapi-host": AMAZON_API_HOST
    }

    # Make the request
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(AMAZON_BASE_URL, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        # Amazon side error
        logging.error(f"[Amazon] HTTP error: {e.response.status_code} {e.response.text}")
        raise ExternalAPIError(f"Amazon HTTP error: {e.response.status_code}") from e
    except Exception as e:
        # Genereal log error
        logging.error(f"[Amazon] request failed: {e}")
        raise ExternalAPIError("Amazon request failed") from e

    # Get the items fron the response
    products = data.get("data", {}).get("products", [])
    
    # Apply limit
    if limit:
        products = products[:limit]
    logging.info(f"[Amazon] fetched {len(products)} items for query='{query}'")

    return {"products": products}

def amazon_to_offer(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert an Amazon API product to an OfferCreate dict.
    """
    return {
        "title": item.get("product_title", ""),
        "last_price": to_decimal(item.get("product_price", "0").replace("$", "").replace(",", "")),
        "currency": normalize_currency(item.get("currency", "USD")),
        "url": item.get("product_url", ""),
        "source": "amazon",
        "source_offer_id": item.get("asin", ""),
        "seller": None,  # Not provided by API
        "image_url": item.get("product_photo"),
        "rating": float(item.get("product_star_rating", 0)) if item.get("product_star_rating") else None,
    }