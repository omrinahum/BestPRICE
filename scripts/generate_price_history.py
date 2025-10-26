"""
Standalone script to generate realistic price history data for watchlist items.

Usage:
    python scripts/generate_price_history.py

This script generates synthetic historical price data for demonstration purposes.
It creates realistic price fluctuations with:
- Stable periods (prices stay same for 2-5 days)
- Gradual trends (slight upward or downward movement)
- Occasional sale events (10-20% drops)
- Random noise for realism
"""

import asyncio
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Add project root to path so we can import backend modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select
from backend.database import async_engine, get_session
from backend.models.users import UserWatchlist
from backend.models.offers import Offer
from backend.models.pricehistory import PriceHistory
from backend.models.search_offer_link import SearchOfferLink  # Import to resolve relationships
from backend.models.searches import Search  # Import to resolve relationships


def generate_realistic_price_history(base_price: float, days: int = 60) -> list[tuple[float, datetime]]:
    """
    Generate realistic price history with stable periods and occasional changes.
    
    Returns:
        List of tuples (price, timestamp) going backwards in time
    """
    price_history = []
    current_date = datetime.utcnow()
    current_price = base_price
    
    # Determine overall trend: -1 (decreasing), 0 (stable), 1 (increasing)
    overall_trend = random.choice([-1, 0, 0, 1])  # Bias towards stable/increasing
    trend_strength = random.uniform(0.0008, 0.002)  # 0.08-0.2% daily trend
    
    # Track if we're in a sale event
    sale_active = False
    sale_end_day = 0
    original_price = current_price
    
    day = 0
    while day < days:
        # Decide how many days to keep this price stable (2-5 days)
        stable_days = random.randint(2, 5)
        
        # Check if we should trigger a sale event (5% chance every period)
        if not sale_active and random.random() < 0.05:
            sale_active = True
            sale_discount = random.uniform(0.10, 0.20)  # 10-20% off
            current_price = original_price * (1 - sale_discount)
            sale_end_day = day + random.randint(3, 7)  # Sale lasts 3-7 days
        
        # End sale if needed
        if sale_active and day >= sale_end_day:
            sale_active = False
            current_price = original_price
        
        # Apply gradual trend (only when not in sale)
        if not sale_active:
            trend_change = overall_trend * trend_strength * stable_days
            current_price *= (1 + trend_change)
            
            # Add small random variation (±0.5%)
            variation = random.uniform(-0.005, 0.005)
            current_price *= (1 + variation)
        
        # Keep price within reasonable bounds (50% to 150% of base)
        current_price = max(base_price * 0.5, min(base_price * 1.5, current_price))
        
        # Store this price for the stable period
        for i in range(stable_days):
            if day + i >= days:
                break
            timestamp = current_date - timedelta(days=days - (day + i))
            price_history.append((round(current_price, 2), timestamp))
        
        # Update original_price for next period (if not in sale)
        if not sale_active:
            original_price = current_price
        
        day += stable_days
    
    return price_history


async def main():
    """
    Main function to generate price history for all watchlist items.
    """
    print("=" * 60)
    print("Price History Generator for BestPRICE")
    print("=" * 60)
    print()
    
    async with async_engine.begin() as conn:
        # Use the connection to create a session
        from sqlalchemy.ext.asyncio import AsyncSession
        async with AsyncSession(bind=conn, expire_on_commit=False) as session:
            # Get all unique offer IDs from watchlists
            print("📋 Finding watchlist items...")
            query = select(UserWatchlist.offer_id).distinct()
            result = await session.execute(query)
            watchlist_offer_ids = result.scalars().all()
            
            if not watchlist_offer_ids:
                print("❌ No watchlist items found!")
                print("   Add some items to your watchlist first, then run this script.")
                return
            
            print(f"✓ Found {len(watchlist_offer_ids)} unique offer(s) in watchlists")
            print()
            
            # Process each offer
            generated_count = 0
            skipped_count = 0
            
            for offer_id in watchlist_offer_ids:
                # Get offer details
                offer_query = select(Offer).where(Offer.id == offer_id)
                offer_result = await session.execute(offer_query)
                offer = offer_result.scalar_one_or_none()
                
                if not offer:
                    print(f"⚠️  Offer ID {offer_id} not found, skipping...")
                    skipped_count += 1
                    continue
                
                # Check if price history already exists and delete it
                history_query = select(PriceHistory).where(PriceHistory.offer_id == offer_id)
                history_result = await session.execute(history_query)
                existing_history = history_result.scalars().all()
                
                if existing_history:
                    print(f"🔄 '{offer.title[:50]}...' - Replacing existing history ({len(existing_history)} records)")
                    # Delete old history
                    for old_record in existing_history:
                        await session.delete(old_record)
                    await session.flush()
                
                # Generate price history
                if not existing_history:
                    print(f"🔄 Generating price history for: '{offer.title[:50]}...'")
                print(f"   Base price: ${offer.last_price} {offer.currency}")
                
                price_points = generate_realistic_price_history(
                    base_price=float(offer.last_price),
                    days=60
                )
                
                # Create PriceHistory records
                price_history_objects = []
                for price, timestamp in price_points:
                    price_history_objects.append(
                        PriceHistory(
                            offer_id=offer.id,
                            price=Decimal(str(price)),
                            currency=offer.currency,
                            fetched_at=timestamp
                        )
                    )
                
                # Add to session
                session.add_all(price_history_objects)
                
                min_price = min(p[0] for p in price_points)
                max_price = max(p[0] for p in price_points)
                print(f"   ✓ Generated {len(price_points)} price points")
                print(f"   📊 Price range: ${min_price:.2f} - ${max_price:.2f}")
                print()
                
                generated_count += 1
            
            # Commit all changes
            if generated_count > 0:
                print("💾 Saving to database...")
                await session.commit()
                print("✓ All data saved successfully!")
            
            # Summary
            print()
            print("=" * 60)
            print("Summary")
            print("=" * 60)
            print(f"✓ Generated price history for: {generated_count} offer(s)")
            if skipped_count > 0:
                print(f"⏭️  Skipped: {skipped_count} offer(s) (not found)")
            print()
            print("🎉 Done! You can now view price history graphs in the app.")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

