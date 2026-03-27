"""Health check endpoints."""
from fastapi import APIRouter
from sqlalchemy import text
from chronosdb.api.dependencies import get_db
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """
    Basic health check.
    
    Returns:
        {"status": "ok"}
    """
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check - verifies database connection.
    
    Used by Kubernetes/Docker to know if service is ready.
    """
    try:
        # Try a simple query
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}