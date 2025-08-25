import os
import base64
import httpx
import logging
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env")) 

EBAY_OAUTH_URL = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
EBAY_SCOPE = "https://api.ebay.com/oauth/api_scope"

EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")


async def get_ebay_token() -> str:
    """
    Fetch eBay OAuth2 token using client_credentials grant type.
    """
    if not EBAY_CLIENT_ID or not EBAY_CLIENT_SECRET:
        raise ValueError("Missing EBAY_CLIENT_ID or EBAY_CLIENT_SECRET in environment")

    # using base64 to encode to ascii only so it could be passed in headers
    auth = base64.b64encode(f"{EBAY_CLIENT_ID}:{EBAY_CLIENT_SECRET}".encode()).decode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth}"
    }

    data = {
        "grant_type": "client_credentials",
        "scope": EBAY_SCOPE
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(EBAY_OAUTH_URL, headers=headers, data=data)
        logging.info(f"eBay token response: {response.text}")
        response.raise_for_status()
        resp_json = response.json()
        return resp_json["access_token"], resp_json.get("expires_in", 3600)
