"""
FastAPI dependencies.

what are dependencies?
- Functions that run before your endpoint
- Provide things your endpoint needs (db session, current user, etc.)
- Automatically injected by FastAPI
"""
from typing import AsyncGenerator
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from chronosdb.db.session import get_db

async def get_current_tenant_id(
        x_tenant_id: int = Header(..., description="Tenant ID from request header")
) -> int:
    """
    Extract tenant ID from request header.

    In production, this would:
    1. Extract API ky from header
    2. Valdate API key
    3. Returned associated tenant_id

    For now, we just read tenant_id directly from header.


    """
    if not x_tenant_id or x_tenant_id < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-Id header is required"
        )
    
    return x_tenant_id

__all__ = ["get_db", "get_current_tenant_id"]