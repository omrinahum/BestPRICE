# backend/routers/user_router.py
"""
User Features Router - Handles watchlist and user-specific functionality
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.schemas.user_schema import WatchlistItemCreate, WatchlistItemResponse
from backend.schemas.search_schema import SearchResponse
from backend.services.user_service import UserService
from backend.repositories.repository import Repository
from backend.database import get_session
from backend.utils.auth import require_current_user_id
from backend.utils.error import ValidationError, NotFoundError

router = APIRouter()

def get_user_service() -> UserService:
    """
    Dependency injection for user service
    """
    return UserService()

def get_repository() -> Repository:
    """
    Dependency injection for repository
    """
    return Repository()

@router.get("/watchlist", response_model=List[WatchlistItemResponse])
async def get_user_watchlist(
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
    current_user_id: int = Depends(require_current_user_id)
):
    """
    Get current user's watchlist items
    """
    # Get current user's watchlist items
    watchlist_items = await user_service.get_user_watchlist(current_user_id, session)
    # Convert watchlist items to response model
    return [WatchlistItemResponse.from_orm(item) for item in watchlist_items]

@router.post("/watchlist", response_model=WatchlistItemResponse)
async def add_to_watchlist(
    watchlist_data: WatchlistItemCreate,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
    current_user_id: int = Depends(require_current_user_id)
):
    """
    Add item to current user's watchlist
    """
    try:
        # Add item to current user's watchlist and save to DB
        watchlist_item = await user_service.add_to_watchlist(current_user_id, watchlist_data, session)
        await session.commit()
        return WatchlistItemResponse.from_orm(watchlist_item)
    except (ValidationError, NotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/watchlist/{item_id}")
async def remove_from_watchlist(
    item_id: int,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
    current_user_id: int = Depends(require_current_user_id)
):
    """
    Remove item from current user's watchlist
    """
    try:
        # Remove item from current user's watchlist and save to DB
        await user_service.remove_from_watchlist(current_user_id, item_id, session)
        await session.commit()
        return {"message": "Item removed from watchlist"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/recent-searches", response_model=List[SearchResponse])
async def get_user_recent_searches(
    limit: int = 10,
    session: AsyncSession = Depends(get_session),
    repository: Repository = Depends(get_repository),
    current_user_id: int = Depends(require_current_user_id)
):
    """
    Get current user's recent searches
    """
    # Get current user's recent searches
    searches = await repository.get_user_recent_searches(current_user_id, session, limit)
    # Convert searches to response model
    return [SearchResponse.from_orm(search) for search in searches]
