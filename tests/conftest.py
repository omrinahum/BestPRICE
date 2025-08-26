import os
import pytest
import asyncio

def pytest_configure():
    """
    Configure pytest settings, DB only for test which deletes after.
    """
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["ASYNC_DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from backend.database import async_engine, Base

@pytest.fixture(scope="session", autouse=True)
def init_test_db():
    """
    Create all tables in the test DB before any tests run.
    """
    # Use asyncio to run the async table creation
    asyncio.run(create_all_tables())

@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield
    if os.path.exists("test.db"):
        os.remove("test.db")

async def create_all_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)