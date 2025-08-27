# backend/adapters/ebay_adapter.py
import time
import logging
from typing import Optional

import httpx

from backend.services.ebay_auth import get_ebay_token
from backend.utils.price import to_decimal, normalize_currency
from backend.utils.error import ExternalAPIError, ValidationError

# Ebay base api GET request struture for Search
EBAY_BASE_URL = "https://api.sandbox.ebay.com/buy/browse/v1/item_summary/search"

# Ebay item condition mapping
EBAY_CONDITION_MAP = {
    "new": 1000,
    "refurbished": 2000,
    "used": 3000
}

# Ebay token data, reusable 
ebay_token_cache: Optional[str] = None
ebay_token_expiry: float = 0

async def get_valid_ebay_token() -> str:
    """
    Get a valid eBay OAuth2 token, refreshing it if necessary.
    """
    global ebay_token_cache, ebay_token_expiry
    current_time = time.time()
    
    try:
        # Check if the token is cached and valid, refreshing if necessary
        if ebay_token_cache is None or current_time >= ebay_token_expiry:
            ebay_token_cache, expires_in = await get_ebay_token()
            ebay_token_expiry = current_time + expires_in - 60
    except Exception as e:
       logging.error(f"Failed to refresh eBay token: {e}")
       raise ExternalAPIError("Could not refresh eBay token") from e

    return ebay_token_cache


def build_ebay_search_url(query: str, limit: int = 50) -> str:
    """
    Build the eBay search URL.
    """
    # Round limit before using
    rounded_limit = round(limit) if limit else 50
    
    url = f"{EBAY_BASE_URL}?q={query}&limit={rounded_limit}"

    return url

async def search_ebay(query: str, limit: int = 50, token: Optional[str] = None) -> dict:
    """
    Execute a search query on eBay.
    """
    if token is None:
        token = await get_valid_ebay_token()

    # Round limit before passing to URL builder
    rounded_limit = round(limit) if limit else 50
    url = build_ebay_search_url(query, rounded_limit)
    headers = {"Authorization": f"Bearer {token}"} 
 
    try:
        # Send the request to eBay API
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            logging.info(f"eBay API raw response: {data}")
            return data
   
    # Handle specific HTTP errors
    except httpx.HTTPStatusError as e:
        # Ebay API returned an error response
        logging.error(f"eBay API HTTP error: {e.response.status_code} {e.response.text}")
        raise ExternalAPIError(f"eBay API HTTP error: {e.response.status_code}") from e
    except Exception as e:
        # General error handling- there was a problem in the request
        logging.error(f"eBay API request failed: {e}")
        raise ExternalAPIError("eBay API request failed") from e

def ebay_to_offer(item: dict) -> dict:
    """
    Convert an eBay item to an OfferCreate object, based on the json format of ebay.
    """
    return {
        "title": item.get("title", ""),
        "last_price": to_decimal(item.get("price", {}).get("value", 0.0)),
        "currency": normalize_currency(item.get("price", {}).get("currency", "USD")),
        "url": item.get("itemWebUrl", ""),
        "source": "ebay",
        "source_offer_id": item.get("itemId", ""),
        "seller": item.get("seller", {}).get("username", None),
        "image_url": item.get("image", {}).get("imageUrl", None),
        "rating": float(item.get("seller", {}).get("feedbackPercentage", 0.0)) if "seller" in item else None
    }


def convert_conditions_for_ebay(conditions: list[str]) -> list[int]:
    """
    Convert a list of item conditions to eBay's internal condition IDs.
    """
    return [EBAY_CONDITION_MAP[c] for c in conditions if c in EBAY_CONDITION_MAP]
