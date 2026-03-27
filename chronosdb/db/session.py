"""Database session management."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from chronosdb.config.settings import settings

# Create async engine
# echo=True will print SQL queries (useful for debugging)
engine = create_async_engine(
    settings.database_url,
    echo=settings.env == "development",  # Only log SQL in dev mode
    future=True,
    pool_pre_ping=True,  # Check connection health before using
)

# Session factory
# This is like a "recipe" for creating database sessions
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get database session.
    
    Usage in FastAPI:
        @app.get("/jobs")
        async def list_jobs(db: AsyncSession = Depends(get_db)):
            # db is automatically injected here
            jobs = await db.execute(select(Job))
            return jobs.scalars().all()
    
    How it works:
    1. Creates a new database session
    2. Yields it to your endpoint
    3. Automatically closes it when endpoint finishes
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()