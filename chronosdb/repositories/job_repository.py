"""Job repository handle job databse operations"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from chronosdb.models.job import Job
from chronosdb.models.step import Step
from chronosdb.config.constants import JobState

class JobRepository:
    """Repository for job model"""

    def __init__(self, db:AsyncSession):
        self.db = db

    async def create(self, job:Job) -> Job:
        """
        Create a new job.
        
        Example:
            job = Job(
                tenant_id=1,
                name="My Job",
                job_type="payment",
                state=JobState.PENDING
            )
            saved = await repo.create(job)
        """
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job 
    
    async def get_by_id(
            self,
            job_id: int,
            tenant_id: int,
            load_steps: bool = False
    ) -> Optional[Job]:
        """
        Find job by ID (tenant-scoped for security).
        
        Args:
            job_id: Job ID
            tenant_id: Tenant ID (ensures user can only see their jobs)
            load_steps: If True, also load related steps
        
        Returns:
            Job if found and belongs to tenant, None otherwise
        """
        query = select(Job).where(
            Job.id == job_id,
            Job.tenant_id == tenant_id
        )

        #Eager oading - load stepa=s in smae query (avoids N+1 problem)
        if load_steps:
            query = query.options(selectinload(Job.steps))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_by_tenant(
        self,
        tenant_id: int,
        state: Optional[JobState] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Job]:
        """
        List jobs for a tenant with optional filters.
        
        Args:
            tenant_id: Tenant ID
            state: Filter by state (optional)
            limit: Max results
            offset: Skip first N results (for pagination)
        
        Returns:
            List of jobs
        
        Example:
            # Get first 10 running jobs
            jobs = await repo.list_by_tenant(
                tenant_id=1,
                state=JobState.RUNNING,
                limit=10
            )
        """
        query = select(Job).where(Job.tenant_id == tenant_id)
        
        if state:
            query = query.where(Job.state == state)
        
        # Pagination
        query = query.limit(limit).offset(offset)
        
        # Order by newest first
        query = query.order_by(Job.created_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update(self, job: Job) -> Job:
        """Update job in database."""
        await self.db.commit()
        await self.db.refresh(job)
        return job
    
    async def update_state(
        self,
        job_id: int,
        tenant_id: int,
        new_state: JobState
    ) -> Optional[Job]:
        """
        Update job state (convenience method).
        
        Args:
            job_id: Job ID
            tenant_id: Tenant ID
            new_state: New state
        
        Returns:
            Updated job or None if not found
        """
        job = await self.get_by_id(job_id, tenant_id)
        
        if not job:
            return None
        
        job.state = new_state
        return await self.update(job)
    

#notes ->
#Eager loading: selectinload() loads relationships efficiently
#Pagination: limit() and offset() for large result sets