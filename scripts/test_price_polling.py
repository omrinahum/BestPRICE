"""
Manual test script to run price polling immediately.

Usage:
    python scripts/test_price_polling.py

This will fetch current prices for all watchlist items and update price history.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.tasks.price_tracker import update_watchlist_prices


async def main():
    """Run price polling manually for testing."""
    print("Running price polling test...")
    print()
    await update_watchlist_prices()
    print()
    print("Test complete!")


if __name__ == "__main__":
    asyncio.run(main())

