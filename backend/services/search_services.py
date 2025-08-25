# backend/services/search_service.py
"""
Service Layer - Contains business logic and orchestration
"""
from typing import Dict, List
import logging
from backend.schemas.search_schema import SearchCreate, SearchResponse
from backend.adapters.ebay_adapter import search_ebay
from backend.adapters.dummyjson_adapter import search_dummyjson, dummyjson_to_offer
from backend.services.data_transformation_service import transform_search_results
from sqlalchemy.ext.asyncio import AsyncSession
from backend.utils.error import ValidationError, NotFoundError, ExternalAPIError

class SearchService:
    def __init__(self, repository, transform_service):
        self.repository = repository
        self.transform_service = transform_service

    async def search_all_sources(self, query: str, filters: dict) -> Dict[str, List[dict]]:
        """
        Search all external sources and return raw results
        """
        results = {}

        # Search eBay
        try:
            ebay_results = await search_ebay(query, filters)
            results['ebay'] = ebay_results.get("itemSummaries", [])
        except Exception as e:
            logging.error(f"eBay search failed: {e}")
            raise ExternalAPIError(f"eBay search failed: {e}")

        # Search DummyJSON
        try:
            dummyjson_results = await search_dummyjson(query, filters)
            results['dummyjson'] = dummyjson_results
        except Exception as e:
            logging.error(f"DummyJSON search failed: {e}")
            raise ExternalAPIError(f"DummyJSON search failed: {e}")

        return results

    

    async def perform_search(self, search_data: SearchCreate, session: AsyncSession) -> SearchResponse:
        """
        Orchestrates the search process - this is the business logic layer
        """
        
        # Check cache, if available in the time limit- uses cached result
        normalized_query = self.repository.normalize_query(search_data.query)
        cached_search = await self.repository.get_cached_offers(normalized_query, max_age_minutes=60, session=session)
        if cached_search:
            print("Using cached results")
            return SearchResponse.from_orm(cached_search)
        
        # Create search record
        search = await self.repository.create_search(search_data, session)

        # Fetch from external APIs
        raw_data = await self.search_all_sources(search.normalized_query, search_data.filters)

        # Transform and validate data
        offers_data = self.transform_service(raw_data)

        # Store results
        await self.repository.update_or_create_offer_with_history(offers_data, search.id, session)

        return SearchResponse.from_orm(search)
    
    async def get_recent_searches(self, session: AsyncSession, limit: int = 10) -> List[SearchResponse]:
        """
        Return most recent searches made
        """
        searches = await self.repository.get_recent_searches(session, limit)
        if not searches:
            return []
        
        return [SearchResponse.from_orm(s) for s in searches]
    
  
 