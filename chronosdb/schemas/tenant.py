"""Pydantic schemas for Tenant API"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TenantCreate(BaseModel):
    """Schema for creating a tenant"""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r'^[a-z0-9-]+$')
    max_concurrent_jobs: Optional[int] = Field(default=10, ge=1, le=1000)
    features: Optional[dict] = Field(default_factory=dict)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Acme Corporation",
                "slug": "acme-corp",
                "max_concurrent_jobs": 50,
                "features": {"ai_retry": False}
            }
        }
    )


class TenantResponse(BaseModel):
    """Schema for tenant API response."""
    id: int
    name: str
    slug: str
    is_active: bool
    max_concurrent_jobs: int
    features: dict
    
    model_config = ConfigDict(from_attributes=True)