"""
Tenant repository - handles tenant database operations.

What is a Repository?
- A class that handles database operations for one model (eg. Tenant)
- Separates "how to query" from "what to do with data"
- Makes code testable
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from chronosdb.models.tenant import Tenant

class TenantRepository:
    """
    Repository for Tenant model.

    Provides methods to:
    - Create Tenants
    - Find by ID or Slug
    - List all tenants
    - Update/delete
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def create(self, tenant: Tenant) -> Tenant:
        """
        create a new Tenant.

        Args:
            tenant: Tenant object to save

        Returns: 
            The saved tenant (with ID populated)

        Example:
            tenant = Tenant(name="Acme Corp", slug="acme")
            saved = await repo.create(tenant)
            print(saved.id)  # Now has ID from database
        """
        self.db.add(tenant)  #Add to session
        await self.db.commit() # save to database
        await self.db.refresh(tenant)
        return tenant
    
    async def get_by_id(self, tenant_id: int) -> Optional[Tenant]:
        """
        Find tenant by ID.
        
        Args:
            tenant_id: Tenant ID to find
        
        Returns:
            Tenant if found, None otherwise
        """
        result = await self.db.execute(
            select(Tenant).where(Tenant.id == tenant_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug:str) -> Optional[Tenant]:
        """
        Find tenant by slug (unique identifier).
        
        Args:
            slug: Tenant slug (e.g., "acme-corp")
        
        Returns:
            Tenant if found, None otherwise
        """
        result = await self.db.execute(
            select(Tenant).where(Tenant.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def list_all(self, active_only: bool = True) -> List[Tenant]:
        """
        List all tenants.
        
        Args:
            active_only: If True, only return active tenants
        
        Returns:
            List of tenants
        """
        query = select(Tenant)
        
        if active_only:
            query = query.where(Tenant.is_active == True)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update(self, tenant: Tenant) -> Tenant:
        """
        Update existing tenant.
        
        Args:
            tenant: Tenant with updated fields
        
        Returns:
            Updated tenant
        """
        await self.db.commit()
        await self.db.refresh(tenant)
        return tenant
    
#notes-> Get results
#result.scalar_one_or_none()  # Single result or None
#result.scalars().all()       # List of results