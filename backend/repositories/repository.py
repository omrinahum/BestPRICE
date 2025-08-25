from typing import List
from backend.models.searches import Search
from backend.models.offers import Offer
from backend.models.pricehistory import PriceHistory
from backend.models.search_offer_link import SearchOfferLink
from backend.schemas.search_schema import SearchCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,desc
from datetime import datetime, timedelta
import re
from backend.utils.error import  ValidationError

class Repository:
    @staticmethod
    def normalize_query(query: str) -> str:
        """
        Normalize the search query by trimming whitespace and lowering the case
        """
        if not query or not isinstance(query, str):
            raise ValidationError("Query must be a non-empty string.")
        return re.sub(r"\s+", " ", query.strip().lower())

    async def create_search(self, search_data: SearchCreate, session: AsyncSession) -> Search:
        """
        Create a new search record
        """
        normalized_query = self.normalize_query(search_data.query)
        search = Search(
            query=search_data.query,
            normalized_query=normalized_query,
            filters=search_data.filters,
        )
        session.add(search)
        await session.flush()
        await session.refresh(search)
        return search

    async def update_or_create_offer_with_history(self, offers_data: List[dict], search_id: int, session: AsyncSession) -> List[Offer]:
        """
        Update existing offers or create new ones with their price history
        """
        offers = []
        price_histories = []
        search_offer_links = []

        # Check for existing offers- sql query to the DB
        for data in offers_data:
            query = select(Offer).where(
                Offer.source == data["source"],
                Offer.source_offer_id == data["source_offer_id"]
            )
            result = await session.execute(query)
            offer = result.scalar_one_or_none()

            # Update existing offer if exists
            if offer:
                offer.last_price = data["last_price"]
                offer.rating = data.get("rating")
                offer.last_seen_at = datetime.utcnow()
                await session.flush()

            # Create new offer if not exists
            else:
                offer = Offer(
                    title=data["title"],
                    last_price=data["last_price"],
                    currency=data["currency"],
                    url=data["url"],
                    source=data["source"],
                    source_offer_id=data["source_offer_id"],
                    seller=data.get("seller"),
                    image_url=data.get("image_url"),
                    rating=data.get("rating"),
                    last_seen_at=None
                )
                # Add new offer to the session
                session.add(offer)
                await session.flush()
            
            # Link offer to search via join table
            search_offer_links.append(SearchOfferLink(
                search_id=search_id,
                offer_id=offer.id
            ))

            # Create price history record
            price_histories.append(PriceHistory(
                offer_id=offer.id,
                price=offer.last_price,
                currency=offer.currency,
            ))
            offers.append(offer)

        # Add all price history records
        session.add_all(search_offer_links)
        session.add_all(price_histories)
        await session.commit()
        return offers

    async def get_recent_searches(self, session: AsyncSession, limit: int = 10) -> List[Search]:
        """
        Return the most recent searches.
        """
        # Validation for limit
        if limit < 1 :
            raise ValidationError("Limit must be atleast 1.")
        
        query=(
            select(Search)
            .order_by(desc(Search.created_at))
            .limit(limit)        
        )
        results = await session.execute(query)
        results = results.scalars().all()
        if not results:
            return []
        
        return results

    async def get_cached_offers(self, normalized_query: str, max_age_minutes: int, session: AsyncSession) -> List[Offer]:
        """
        Get the most recent search for the same query (caching logic).
        Returns the Search object if cache is valid, else None.
        """
        # Find the most recent search with the same query
        query = (
            select(Search)
            .where(Search.normalized_query == normalized_query)
            .order_by(desc(Search.created_at))
            .limit(1)
        )

        result = await session.execute(query)
        search = result.scalar_one_or_none()

        if not search:
            return []

        if search.created_at < datetime.utcnow() - timedelta(minutes=max_age_minutes):
            return []

        return search
    
