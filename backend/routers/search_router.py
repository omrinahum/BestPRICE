# backend/routers/search_router.py
"""
Controller Layer - Handles HTTP requests and dependency injection
"""
from fastapi import APIRouter, Depends
from typing import List
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from backend.schemas.search_schema import SearchResponse, SearchCreate
from backend.services.search_services import SearchService
from backend.repositories.repository import Repository
from backend.services.data_transformation_service import transform_search_results
from backend.database import get_session
from backend.utils.error import handle_api_errors


router = APIRouter()

def get_search_service() -> SearchService:
    """
    Dependency injection for search service
    """
    return SearchService(
        repository=Repository(),
        transform_service=transform_search_results
    )

@router.get("/recent", response_model= List[SearchResponse])
async def recent_searches(limit: int = 10, session: AsyncSession = Depends(get_session),
                          search_service: SearchService = Depends(get_search_service)):
    """
    Get recent searches.
    """
    return await search_service.get_recent_searches(session, limit)

@router.post("/", response_model=SearchResponse)
async def create_search(search_data: SearchCreate, session: AsyncSession = Depends(get_session),
                        search_service: SearchService = Depends(get_search_service)) -> SearchResponse:
    """
    Create a new search and return results
    """
    return await search_service.perform_search(search_data, session)
   
   
    
