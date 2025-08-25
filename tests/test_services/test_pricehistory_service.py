
import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from datetime import datetime
from backend.services.pricehistory_service import get_price_history_for_offer
from backend.utils.error import NotFoundError

@pytest.mark.asyncio
async def test_get_price_history_for_offer_success():
    """
    get_price_history_for_offer: returns list of PriceHistoryResponse from DB rows.
    """
    session = MagicMock()
    # Create a fake DB row
    row = MagicMock(id=1, offer_id=1, price=10.0, fetched_at=datetime.utcnow(), currency="USD")
    result = MagicMock()
    result.scalars.return_value.all.return_value = [row]
    session.execute = AsyncMock(return_value=result)

    history = await get_price_history_for_offer(1, session)

    # Check that get_price_history_for_offer returns the expected type and result
    assert isinstance(history, list) and len(history) == 1
    assert history[0].id == 1
    assert history[0].price == 10.0
    assert history[0].currency == "USD"

@pytest.mark.asyncio
async def test_get_price_history_for_offer_not_found():
    """
    get_price_history_for_offer: returns an empty list when no history is found.
    """
    session = MagicMock()
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=result)

    history = await get_price_history_for_offer(42, session)
    assert history == []
