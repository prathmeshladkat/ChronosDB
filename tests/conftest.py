"""
Pytest configuration and fixtures.

Fixtures are reusable test components.
"""
import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from chronosdb.models.base import Base
from chronosdb.config.settings import settings

# Use in-memory SQLite for tests (fast!)
TEST_DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_Hi4bdNPXxt3a@ep-bitter-math-am2upr46-pooler.c-5.us-east-1.aws.neon.tech/neondb?ssl=require"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.
    
    This ensures tests don't interfere with each other.
    """
    # Create engine
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()