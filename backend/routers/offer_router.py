from fastapi import APIRouter, Depends
from backend.services.offer_service import get_offers_for_search
from backend.services.pricehistory_service import get_price_history_for_offer
from backend.schemas.offer_schema import OfferResponse
from backend.schemas.pricehistory_schema import PriceHistoryResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_session


router = APIRouter()

@router.get("/", response_model=list[OfferResponse])
async def offers(search_id: int, page: int = 1, page_size: int = 20, sort_by: str = "last_price",
                 sort_order: str = "asc", session: AsyncSession = Depends(get_session)):
    """
    Fetch offers for a specific search ID with pagination.
    """
    return await get_offers_for_search(search_id, session, page, page_size, sort_by, sort_order)

@router.get("/price/{offer_id}", response_model=list[PriceHistoryResponse])
async def offer_price_history(offer_id: int, session: AsyncSession = Depends(get_session)):
    """
    Fetch price history for a specific offer ID.
    """
    return await get_price_history_for_offer(offer_id, session)
