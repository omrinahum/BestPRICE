from sqlalchemy import select
from backend.models.pricehistory import PriceHistory
from backend.schemas.pricehistory_schema import PriceHistoryResponse
from backend.utils.error import NotFoundError

async def get_price_history_for_offer(offer_id: int, session) -> list[PriceHistoryResponse]:
    """
    Fetch price history records for a specific offer.
    """
    query = (
        select(PriceHistory)
        .where(PriceHistory.offer_id == offer_id)
        .order_by(PriceHistory.fetched_at)
    )
    result = await session.execute(query)
    history = result.scalars().all()
    if not history:
        return []
    
    return [PriceHistoryResponse.from_orm(h) for h in history]
