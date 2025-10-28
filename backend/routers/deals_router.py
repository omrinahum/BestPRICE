# backend/routers/deals_router.py
"""
Controller Layer - Handles best deals HTTP requests
"""
from fastapi import APIRouter, Depends, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.schemas.deal_schema import DealResponse
from backend.services.deals_service import get_recent_best_deals
from backend.database import get_session

router = APIRouter()

@router.get("/recent", response_model=List[DealResponse])
async def get_recent_deals(
    limit: int = Query(15, ge=1, le=50, description="Number of deals to return"),
    hours: int = Query(48, ge=24, le=168, description="Time window in hours"),
    session: AsyncSession = Depends(get_session)
):
    """
    Get the best deals from recent searches
    
    Analyzes searches from the last N hours and returns top deals
    No authentication required, public endpoint
    """
    deals = await get_recent_best_deals(session, limit=limit, hours=hours)
    return deals

