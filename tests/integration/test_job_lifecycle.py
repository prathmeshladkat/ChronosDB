"""Integration tests for job lifecycle."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from chronosdb.models.tenant import Tenant
from chronosdb.models.job import Job
from chronosdb.models.step import Step
from chronosdb.services.job_service import JobService
from chronosdb.schemas.job import JobCreate, StepConfig
from chronosdb.config.constants import JobState, StepState


@pytest.mark.asyncio
async def test_create_job_with_steps(db_session: AsyncSession):
    """Test creating a job with steps."""
    # Create tenant first
    tenant = Tenant(name="Test Org", slug="test", is_active=True)
    db_session.add(tenant)
    await db_session.commit()
    
    # Create job via service
    service = JobService(db_session)
    
    job_data = JobCreate(
        name="Test Job",
        job_type="test",
        steps=[
            StepConfig(name="Step 1", task_type="test_task", config={}),
            StepConfig(name="Step 2", task_type="test_task", config={}),
        ]
    )
    
    job = await service.create_job(tenant.id, job_data)
    
    # Assertions
    assert job.id is not None
    assert job.name == "Test Job"
    assert job.state == JobState.PENDING
    assert len(job.steps) == 2
    assert job.steps[0].order == 0
    assert job.steps[1].order == 1


@pytest.mark.asyncio
async def test_start_job(db_session: AsyncSession):
    """Test starting a job."""
    # Setup
    tenant = Tenant(name="Test Org", slug="test", is_active=True)
    db_session.add(tenant)
    await db_session.commit()
    
    service = JobService(db_session)
    job_data = JobCreate(
        name="Test Job",
        job_type="test",
        steps=[StepConfig(name="Step 1", task_type="test", config={})]
    )
    job = await service.create_job(tenant.id, job_data)
    
    # Start job
    started_job = await service.start_job(job.id, tenant.id)
    
    # Assertions
    assert started_job.state == JobState.RUNNING
    assert started_job.started_at is not None