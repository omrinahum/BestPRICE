# backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator

DATABASE_URL = "sqlite:///./bestprice.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Use aiosqlite for async engine
ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./bestprice.db"
async_engine = create_async_engine(ASYNC_DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
