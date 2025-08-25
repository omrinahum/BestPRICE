# backend/init_db.py
import asyncio

from backend.database import async_engine, Base
from backend.models import offers, pricehistory, searches, search_offer_link

async def async_init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(async_init_db())
