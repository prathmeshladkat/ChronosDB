"""Tenant service - buisness logic for tenant managment."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from chronosdb.models.tenant import Tenant
from chronosdb.repositories.tenant_repository import TenantRepository
from chronosdb.schemas.tenant import TenantCreate

class TenantService:
    """
    Service for tenant operations

    Why use a service?
    - Encapsulates buisness logic
    - Can use multiple repositories
    - Handles validations, errors etc.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TenantRepository(db)

    async def create_tenant(self, data: TenantCreate) -> Tenant:
        """
        create a new tenant with validation

        Args:
            data: Tenant creation data (from api)

        Returns:
            Created Tenant

        Raises:
            ValueError: If slug already exists
        """

        #check if slug is unique
        existing = await self.repo.get_by_slug(data.slug)
        if existing:
            raise ValueError(f"Tenant with slug '{data.slug}' already exists")
        
        #create tenant model from schema
        tenant = Tenant(
            name=data.name,
            slug=data.slug,
            is_active=True,
            max_concurrent_jobs=data.max_concurrent_jobs or 10,
            features=data.features or {},
        )

        return await self.repo.create(tenant)
    
    async def get_tenant(self, tenant_id: int) -> Optional[Tenant]:
        return await self.repo.get_by_id(tenant_id)