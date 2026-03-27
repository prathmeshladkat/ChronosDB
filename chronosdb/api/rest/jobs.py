"""Job REST API endpoints"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from chronosdb.api.dependencies import get_db, get_current_tenant_id
from chronosdb.services.job_service import JobService
from chronosdb.schemas.job import JobCreate, JobResponse
from chronosdb.config.constants import JobState

router =APIRouter(prefix="/jobs", tags=["jobs"])

@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job"
)
async def create_job(
    data: JobCreate,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new job with steps.
    
    Example:
```
    POST /jobs
    Headers: X-Tenant-Id: 1
    
    {
        "name": "Payment Processing",
        "job_type": "payment",
        "steps": [
            {"name": "Validate", "task_type": "validation"},
            {"name": "Process", "task_type": "execution"}
        ]
    }
```
    """
    service = JobService(db)
    job = await service.create_job(tenant_id, data)
    return job

@router.post(
    "/{job_id}/start",
    response_model=JobResponse,
    summary="Start job execution"
)
async def start_job(
    job_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a pending job.

    Example:
```
    POST /jobs/123/start
    Header: X-Tenant-Id: 1
```
    """
    service = JobService(db)

    try:
        job = await service.start_job(job_id, tenant_id)
        return job
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = str(e)
        )
    
@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get a job status"
)
async def get_job(
    job_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get job details and status.
    
    Example:
```
    GET /jobs/123
    Headers: X-Tenant-Id: 1
```
    """
    service = JobService(db)
    job = await service.get_job(job_id, tenant_id, include_steps=True)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    return job


@router.get(
    "",
    response_model=List[JobResponse],
    summary="List jobs"
)
async def list_jobs(
    state: Optional[JobState] = Query(None, description="Filter by state"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """
    List jobs for tenant.
    
    Example:
```
    GET /jobs?state=RUNNING&limit=10
    Headers: X-Tenant-Id: 1
```
    """
    service = JobService(db)
    jobs = await service.list_jobs(tenant_id, state, limit, offset)
    return jobs
