"""Job service - business logic for job management."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from chronosdb.models.job import Job
from chronosdb.models.step import Step
from chronosdb.repositories.job_repository import JobRepository
from chronosdb.repositories.step_repository import StepRepository
from chronosdb.core.state_machine import JobStateMachine, StepStateMachine
from chronosdb.schemas.job import JobCreate
from chronosdb.config.constants import JobState, StepState, StepType

class JobService:
    """
    Service for job operations.
    
    Handles:
    - Creating jobs with steps
    - Starting job execution
    - State transitions
    """

    def __init__(self, db:AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
        self.step_repo = StepRepository(db)

    async def create_job(self, tenant_id: int, data: JobCreate) -> Job:
        """
        Create a new job with steps.
        
        Args:
            tenant_id: Tenant ID (from auth)
            data: Job creation data
        
        Returns:
            Created job with steps
        
        Example:
            job_data = JobCreate(
                name="Payment Processing",
                job_type="payment",
                steps=[
                    StepConfig(name="Validate", task_type="validation"),
                    StepConfig(name="Process", task_type="execution"),
                ]
            )
            job = await service.create_job(tenant_id=1, data=job_data)
        """

        #Create job
        job = Job(
            tenant_id=tenant_id,
            name=data.name,
            job_type=data.job_type,
            state=JobState.PENDING,
            config=data.config,
            max_retries=data.max_retries,
            retry_policy=data.retry_policy,
            priority=data.priority,
            tags=data.tags,
            trigger_type=data.trigger_type,
            agent_context=data.agent_context,
        )

        job = await self.job_repo.create(job)

        #Create steps
        steps = []
        for i, step_config in enumerate(data.steps):
            step = Step(
                job_id=job.id,
                name=step_config.name,
                order=i,  # Sequential order
                state=StepState.PENDING,
                step_type=StepType(step_config.step_type),
                task_type=step_config.task_type,
                config=step_config.config,
                max_retries=step_config.max_retries,
                timeout_seconds=step_config.timeout_seconds,
                llm_config=step_config.llm_config,
                decision_logic=step_config.decision_logic,
            )
            steps.append(step)
        
        await self.step_repo.create_many(steps)
        
        # Reload job with steps
        return await self.job_repo.get_by_id(job.id, tenant_id, load_steps=True)
    
    async def start_job(self, job_id: int, tenant_id: int) -> Job:
        """
        Start job execution.
        
        Args:
            job_id: Job ID
            tenant_id: Tenant ID
        
        Returns:
            Updated job
        
        Raises:
            ValueError: If job not found or invalid state transition
        """
        job = await self.job_repo.get_by_id(job_id, tenant_id)
        
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Validate state transition using state machine
        new_state = JobStateMachine.transition(job.state, JobState.RUNNING)
        
        # Update job
        job.state = new_state
        job.started_at = datetime.utcnow()
        
        return await self.job_repo.update(job)
    
    async def get_job(
        self,
        job_id: int,
        tenant_id: int,
        include_steps: bool = False
    ) -> Optional[Job]:
        """
        Get job by ID.
        
        Args:
            job_id: Job ID
            tenant_id: Tenant ID (security)
            include_steps: Load steps too?
        
        Returns:
            Job if found, None otherwise
        """
        return await self.job_repo.get_by_id(job_id, tenant_id, load_steps=include_steps)
    
    async def list_jobs(
        self,
        tenant_id: int,
        state: Optional[JobState] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Job]:
        """List jobs for tenant with optional filters."""
        return await self.job_repo.list_by_tenant(
            tenant_id=tenant_id,
            state=state,
            limit=limit,
            offset=offset
        )
