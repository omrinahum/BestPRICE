
import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from datetime import datetime
from backend.services.offer_service import get_offers_for_search
from backend.utils.error import ValidationError, NotFoundError

@pytest.mark.asyncio
async def test_get_offers_for_search_validation():
    """
    get_offers_for_search: validates pagination arguments and raises ValidationError.
    """
    session = MagicMock()
    # Check that pagination arguments are validated
    with pytest.raises(ValidationError):
        await get_offers_for_search(1, session, page=0, page_size=10)
    with pytest.raises(ValidationError):
        await get_offers_for_search(1, session, page=1, page_size=0)
    with pytest.raises(ValidationError):
        await get_offers_for_search(1, session, page=1, page_size=1000)

@pytest.mark.asyncio
async def test_get_offers_for_search_success():
    """
    get_offers_for_search: returns list of OfferResponse from DB rows.
    """
    session = MagicMock()
    # Build a fake offer response
    offer = MagicMock(
        id=1, title="Test", last_price=Decimal("19.99"), currency="USD", url="http://x", source="ebay",
        source_offer_id="1", created_at=datetime.utcnow(), rating=5, seller="seller", image_url="http://image.url"
    )
    result = MagicMock()
    result.scalars.return_value.all.return_value = [offer]
    session.execute = AsyncMock(return_value=result)

    offers = await get_offers_for_search(1, session, page=1, page_size=10, sort_by="last_price", sort_order="asc")

    # Check that get_offers_for_search returns the expected type and result
    assert isinstance(offers, list) and len(offers) == 1
    assert offers[0].title == "Test"

@pytest.mark.asyncio
async def test_get_offers_for_search_not_found():
    """
    get_offers_for_search: returns an empty list when no offers are found.
    """
    session = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=result)

    offers = await get_offers_for_search(99, session, page=1, page_size=10)
    assert offers == []
