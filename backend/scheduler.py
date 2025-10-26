"""
Background scheduler for periodic tasks.

This module sets up scheduled tasks like price tracking for watchlist items.
"""

import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.tasks.price_tracker import update_watchlist_prices

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_scheduler():
    """
    Start the background scheduler with all periodic tasks.
    
    Tasks:
    - Price tracking: Runs daily at 2:00 AM
    """
    scheduler = AsyncIOScheduler()
    
    # Schedule price tracking task to run daily at 2 AM
    scheduler.add_job(
        update_watchlist_prices,
        trigger=CronTrigger(hour=2, minute=0),
        id='update_watchlist_prices',
        name='Update watchlist prices',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("✓ Scheduler started - Price tracking will run daily at 2:00 AM")
    
    return scheduler


def stop_scheduler(scheduler):
    """Stop the scheduler gracefully."""
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler stopped")

