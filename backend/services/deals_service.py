# backend/services/deals_service.py
"""
Service Layer - Best Deals business logic
Analyzes recent searches to find the best deals based on price, rating, and recency
"""
import statistics
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.searches import Search
from backend.models.offers import Offer
from backend.models.search_offer_link import SearchOfferLink
from decimal import Decimal

# Configure logging
logger = logging.getLogger(__name__)


async def get_recent_best_deals(session: AsyncSession, limit: int = 15, hours: int = 48) -> List[Dict[str, Any]]:
    """
    Find the best deals from recent searches
    
    Algorithm:
    1. Get all searches from last N hours
    2. Group offers by normalized_query
    3. For each group:
       a. Remove low-price outliers 
       b. Calculate avg_price and std_dev using filtered prices
       c. Min 5 offers required per group
    4. Score each offer using z-score approach (standard deviations below average)
    5. Calculate Meta-Score: 60% discount + 30% rating + 10% recency
    6. Select top 3 candidates per query group
    7. Rank all candidates globally and return top N deals
    
    Returns:
        List of deal dictionaries with offer data + metadata
    """
    # Calculate cutoff time
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    # 1+2: Get all unique normalized queries from recent searches
    query_stmt = (
        select(Search.normalized_query)
        .where(Search.created_at >= cutoff_time)
        .distinct()
    )
    result = await session.execute(query_stmt)
    normalized_queries = result.scalars().all()
    
    if not normalized_queries:
        return []
    
    # 3: Process each query group
    all_candidates = []
    
    for normalized_query in normalized_queries:
        # Get all offers for this query group with their search dates
        offers_stmt = (
            select(Offer, func.max(Search.created_at).label('search_date'))
            .join(SearchOfferLink, Offer.id == SearchOfferLink.offer_id)
            .join(Search, SearchOfferLink.search_id == Search.id)
            .where(
                and_(
                    Search.normalized_query == normalized_query,
                    Search.created_at >= cutoff_time
                )
            )
            .group_by(Offer.id)
        )
        offers_result = await session.execute(offers_stmt)
        offers_with_dates = offers_result.all()
        
        # Skip if less than 5 offers in this group
        if len(offers_with_dates) < 5:
            continue
        
        # Extract offers and calculate statistics
        offers = [row[0] for row in offers_with_dates]
        prices = [float(offer.last_price) for offer in offers]
        
        # Remove low-price outliers using median method before calculating statistics
        # This prevents cheap accessories from skewing the average
        filtered_prices = remove_low_price_outliers(prices)
        
        # Use filtered prices for statistics
        avg_price = statistics.mean(filtered_prices)
        std_dev = statistics.stdev(filtered_prices) if len(filtered_prices) > 1 else 0
        
        # Create a set of filtered prices for quick lookup
        filtered_price_set = set(filtered_prices)
        
        # 4: Score each offer in this group (if not filtered out)
        scored_offers = []
        for offer, search_date in offers_with_dates:
            offer_price = float(offer.last_price)
            
            # Skip offers that were filtered out as low-price outliers
            if offer_price not in filtered_price_set:
                continue
            # Calculate discount score (60% weight) using standard deviation
            discount_score = calculate_discount_score(
                float(offer.last_price), 
                avg_price, 
                std_dev
            )
            
            # 5: Calculate rating score
            # Calculate rating score (30% weight)
            rating_score = calculate_rating_score(offer.rating)
            
            # Calculate recency score (10% weight)
            recency_score = calculate_recency_score(search_date)
            
            # Meta-Score = weighted sum
            meta_score = (discount_score * 0.60) + (rating_score * 0.30) + (recency_score * 0.10)
            
            # Calculate discount percentage for display
            discount_pct = ((avg_price - float(offer.last_price)) / avg_price * 100) if avg_price > 0 else 0
            
            scored_offers.append({
                'offer': offer,
                'meta_score': meta_score,
                'avg_price': Decimal(str(round(avg_price, 2))),
                'discount_percentage': round(discount_pct, 2),
                'search_date': search_date
            })
        
        # 6: Get top 3 candidates from this query group
        scored_offers.sort(key=lambda x: x['meta_score'], reverse=True)
        all_candidates.extend(scored_offers[:3])
    
    # 7: Global ranking and deduplication
    all_candidates.sort(key=lambda x: x['meta_score'], reverse=True)
    
    # Deduplicate by (source, source_offer_id)
    seen = set()
    unique_deals = []
    
    for candidate in all_candidates:
        offer = candidate['offer']
        key = (offer.source, offer.source_offer_id)
        
        if key not in seen:
            seen.add(key)
            
            # Build response dictionary
            deal = {
                'id': offer.id,
                'title': offer.title,
                'last_price': offer.last_price,
                'currency': offer.currency,
                'url': offer.url,
                'source': offer.source,
                'source_offer_id': offer.source_offer_id,
                'seller': offer.seller,
                'image_url': offer.image_url,
                'rating': float(offer.rating) if offer.rating else None,
                'created_at': offer.created_at,
                'meta_score': round(candidate['meta_score'], 4),
                'avg_price': candidate['avg_price'],
                'discount_percentage': candidate['discount_percentage'],
                'search_date': candidate['search_date']
            }
            unique_deals.append(deal)
            
            if len(unique_deals) >= limit:
                break
    
    return unique_deals


def remove_low_price_outliers(prices: List[float]) -> List[float]:
    """
    Remove low-price outliers using median-based filtering
    Prevents cheap accessories from skewing the average 
    Method:
    - Calculate the median price
    - Remove prices that are less than 35% of the median
    - This effectively filters out accessories while keeping main products

    Returns:
        Filtered list of prices with low outliers removed
        Falls back to original prices if insufficient data
    """
    # Need at least 5 data points
    if len(prices) < 5:
        return prices
    
    # Calculate median
    sorted_prices = sorted(prices)
    n = len(sorted_prices)
    median_index = n // 2
    
    if n % 2 == 0:
        # Even number: average of two middle values
        median = (sorted_prices[median_index - 1] + sorted_prices[median_index]) / 2
    else:
        # Odd number: middle value
        median = sorted_prices[median_index]
    
    # If median is very low, don't filter (all items are cheap)
    if median < 10:
        return prices
    
    # Set threshold: keep prices >= 35% of median
    # This more aggressively filters out cheap accessories
    threshold = median * 0.35
    
    # Filter out low-price outliers
    filtered = [p for p in prices if p >= threshold]
    
    # Safety checks:
    # If we filtered out too many (>50%), use original
    if len(filtered) < len(prices) * 0.5:
        return prices
    
    # If we end up with too few prices (< 3), fall back to original
    if len(filtered) < 3:
        return prices
    
    return filtered


def calculate_discount_score(offer_price: float, avg_price: float, std_dev: float) -> float:
    """
    Calculate discount score using standard deviation (z-score approach)
       
    Returns:
        Discount score (normalized 0-1, where 1 = excellent deal)
    """
    if avg_price <= 0:
        return 0.0
    
    # If std_dev is 0 (all prices identical), fall back to percentage discount
    if std_dev == 0:
        discount = (avg_price - offer_price) / avg_price
        return max(0.0, discount)
    
    # Calculate z-score: how many std devs below the mean
    z_score = (avg_price - offer_price) / std_dev
    
    # Normalize z-score to 0-1 range
    normalized_score = z_score / 2.0
    
    # Clamp between 0 and 1
    return max(0.0, min(1.0, normalized_score))


def calculate_rating_score(rating: float) -> float:
    """
    Normalize rating to 0-1 scale
    Rating scale is 0-5
    Returns:
        Normalized rating score (0-1)
    """
    if rating is None:
        return 0.0
    
    return float(rating) / 5.0


def calculate_recency_score(search_date: datetime) -> float:
    """
    Calculate recency score with 24h boost and 24-48h decay
    Returns:
        Recency score (0-1)
    """
    now = datetime.utcnow()
    hours_old = (now - search_date).total_seconds() / 3600
    
    if hours_old <= 24:
        return 1.0
    elif hours_old <= 48:
        return (48 - hours_old) / 24
    else:
        return 0.0

