"""Step repository - handles step database operations"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from chronosdb.models.step import Step
from chronosdb.config.constants import StepState

class StepRepository:
    """Repositoyry from Step model."""

    def __init__(self, db: AsyncSession):
        self.db = db


    async def create(self, step: Step) -> Step:
        """Create a new step"""
        self.db.add(step)
        await self.db.commit()
        await self.db.refresh(step)
        return step
    
    async def create_many(self, steps: List[Step]) -> List[Step]:
        """
        Create multiple steps at once (bulk insert).
        
        More efficient than creating one by one.
        
        Example:
            steps = [
                Step(job_id=1, name="Step 1", order=0),
                Step(job_id=1, name="Step 2", order=1),
            ]
            await repo.create_many(steps)
        """
        self.db.add_all(steps)
        await self.db.commit()

        #Refresh all to get IDs
        for step in steps:
            await self.db.refresh(step)

        return steps
    
    async def get_by_id(self, step_id: int) -> Optional[Step]:
        """Find step by ID"""
        result = await self.db.execute(
            select(Step).where(Step.id == step_id)
        )
        return result.scalar_one_or_none()
    
    async def list_by_job(self, job_id: int) -> List[Step]:
        """
        Get all steps for a job, ordered by execution order.
        
        Args:
            job_id: Job ID
        
        Returns:
            List of steps in execution order
        """
        result = await self.db.execute(
            select(Step)
            .where(Step.job_id == job_id)
            .order_by(Step.order)  # Execute in correct order
        )
        return list(result.scalars().all())
    
    async def get_next_pending_step(self, job_id: int) -> Optional[Step]:
        """
        Find the next step that needs to run.
        
        Returns the first PENDING step (by order).
        """
        result = await self.db.execute(
            select(Step)
            .where(
                Step.job_id == job_id,
                Step.state == StepState.PENDING
            )
            .order_by(Step.order)
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def update(self, step: Step) -> Step:
        """Update step."""
        await self.db.commit()
        await self.db.refresh(step)
        return step