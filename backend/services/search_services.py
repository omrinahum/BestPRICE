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

    async def search_all_sources(self, query: str) -> Dict[str, List[dict]]:
        """
        Search all external sources and return raw results
        """
        results = {}

        # Search eBay (optional - skip if credentials not available)
        try:
            ebay_results = await search_ebay(query) 
            ebay_items = ebay_results.get("itemSummaries", [])
            results['ebay'] = ebay_items
            logging.info(f"eBay search successful: {len(ebay_items)} items")
        except Exception as e:
            logging.warning(f"eBay search failed (skipping): {e}")
            results['ebay'] = []

        # Search DummyJSON
        try:
            dummyjson_results = await search_dummyjson(query) 
            dummy_items = dummyjson_results.get("products", [])
            dummyjson_results["items_filtered"] = dummy_items
            results['dummyjson'] = dummyjson_results
            logging.info(f"DummyJSON search successful: {len(dummy_items)} items")
        except Exception as e:
            logging.warning(f"DummyJSON search failed (skipping): {e}")
            results['dummyjson'] = []

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
        raw_data = await self.search_all_sources(search.normalized_query)

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
    
  
 