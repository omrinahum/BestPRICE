"""
Background task to track prices for watchlist items.

This task polls external APIs to get current prices for items in user watchlists
and updates the price history accordingly.
"""

import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import async_engine
from backend.models.users import UserWatchlist
from backend.models.offers import Offer
from backend.models.pricehistory import PriceHistory
from backend.models.search_offer_link import SearchOfferLink  # Import to resolve relationships
from backend.models.searches import Search  # Import to resolve relationships
from backend.adapters.ebay_adapter import search_ebay, ebay_to_offer
from backend.adapters.dummyjson_adapter import search_dummyjson, dummyjson_to_offer
from backend.adapters.amazon_adapter import search_amazon, amazon_to_offer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_current_price_from_api(offer: Offer) -> dict | None:
    """
    Fetch current price for an offer from its source API.
    
    Args:
        offer: The offer to fetch price for
        
    Returns:
        Dict with updated price info, or None if not found
    """
    try:
        # Search by title to find the item
        search_query = offer.title[:50]  # Use first 50 chars of title
        
        if offer.source == 'ebay':
            results = await search_ebay(search_query)
            items = results.get('itemSummaries', [])
            
            # Try to find the exact item by matching source_offer_id
            for item in items:
                if item.get('itemId') == offer.source_offer_id:
                    return ebay_to_offer(item)
            
            # If not found by ID, use first result (best match)
            if items:
                return ebay_to_offer(items[0])
                
        elif offer.source == 'dummyjson':
            results = await search_dummyjson(search_query)
            products = results.get('products', [])
            
            # Try to find exact match
            for product in products:
                if str(product.get('id')) == offer.source_offer_id:
                    return dummyjson_to_offer(product)
            
            # Use first result
            if products:
                return dummyjson_to_offer(products[0])
                
        elif offer.source == 'amazon':
            results = await search_amazon(search_query)
            products = results.get('products', [])
            
            # Try to find exact match
            for product in products:
                if product.get('asin') == offer.source_offer_id:
                    return amazon_to_offer(product)
            
            # Use first result
            if products:
                return amazon_to_offer(products[0])
        
        return None
        
    except Exception as e:
        logger.error(f"Error fetching price for offer {offer.id} from {offer.source}: {e}")
        return None


async def update_watchlist_prices():
    """
    Main task to update prices for all watchlist items.
    This should be run daily via scheduler.
    """
    logger.info("=" * 60)
    logger.info("Starting watchlist price update task")
    logger.info("=" * 60)
    
    async with async_engine.begin() as conn:
        async with AsyncSession(bind=conn, expire_on_commit=False) as session:
            # Get all unique offers in watchlists
            query = select(UserWatchlist.offer_id).distinct()
            result = await session.execute(query)
            offer_ids = result.scalars().all()
            
            if not offer_ids:
                logger.info("No watchlist items found")
                return
            
            logger.info(f"Found {len(offer_ids)} unique offer(s) in watchlists")
            
            updated_count = 0
            failed_count = 0
            unchanged_count = 0
            
            for offer_id in offer_ids:
                try:
                    # Get offer details
                    offer_query = select(Offer).where(Offer.id == offer_id)
                    offer_result = await session.execute(offer_query)
                    offer = offer_result.scalar_one_or_none()
                    
                    if not offer:
                        logger.warning(f"Offer {offer_id} not found")
                        failed_count += 1
                        continue
                    
                    logger.info(f"Checking price for: {offer.title[:50]}...")
                    
                    # Fetch current price from API
                    updated_data = await fetch_current_price_from_api(offer)
                    
                    if not updated_data:
                        logger.warning(f"  Could not fetch price from {offer.source}")
                        failed_count += 1
                        continue
                    
                    new_price = Decimal(str(updated_data['last_price']))
                    old_price = offer.last_price
                    
                    # Check if price changed
                    if new_price == old_price:
                        logger.info(f"  Price unchanged: ${old_price}")
                        unchanged_count += 1
                        # Still add to history to track that we checked
                        price_history = PriceHistory(
                            offer_id=offer.id,
                            price=new_price,
                            currency=offer.currency,
                            fetched_at=datetime.utcnow()
                        )
                        session.add(price_history)
                    else:
                        # Price changed - update offer and add to history
                        logger.info(f"  Price changed: ${old_price} → ${new_price}")
                        offer.last_price = new_price
                        offer.last_seen_at = datetime.utcnow()
                        
                        price_history = PriceHistory(
                            offer_id=offer.id,
                            price=new_price,
                            currency=offer.currency,
                            fetched_at=datetime.utcnow()
                        )
                        session.add(price_history)
                        updated_count += 1
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing offer {offer_id}: {e}")
                    failed_count += 1
                    continue
            
            # Commit all changes
            await session.commit()
            
            # Summary
            logger.info("")
            logger.info("=" * 60)
            logger.info("Price Update Summary")
            logger.info("=" * 60)
            logger.info(f"✓ Prices updated: {updated_count}")
            logger.info(f"→ Prices unchanged: {unchanged_count}")
            logger.info(f"✗ Failed: {failed_count}")
            logger.info("=" * 60)


async def main():
    """Run the price update task manually."""
    await update_watchlist_prices()


if __name__ == "__main__":
    # For manual testing
    asyncio.run(main())

