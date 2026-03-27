"""Pydantic schemas for Job API."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from chronosdb.config.constants import JobState, TriggerType


class StepConfig(BaseModel):
    """Configuration for a step in job creation."""
    name: str
    task_type: str
    config: dict = Field(default_factory=dict)
    step_type: str = "TASK"
    max_retries: int = 3
    timeout_seconds: Optional[int] = None
    
    # AI-specific (optional)
    llm_config: Optional[dict] = None
    decision_logic: Optional[dict] = None


class JobCreate(BaseModel):
    """Schema for creating a new job."""
    name: str = Field(..., min_length=1, max_length=255)
    job_type: str = Field(..., min_length=1, max_length=100)
    config: dict = Field(default_factory=dict)
    steps: List[StepConfig] = Field(..., min_items=1)
    
    # Optional
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_policy: str = "exponential_backoff"
    priority: int = Field(default=5, ge=1, le=10)
    tags: List[str] = Field(default_factory=list)
    
    # AI agent context (if triggered by AI)
    trigger_type: TriggerType = TriggerType.MANUAL
    agent_context: Optional[dict] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Payment Retry Pipeline",
                "job_type": "payment_processing",
                "config": {"customer_id": "cust_123"},
                "steps": [
                    {
                        "name": "Validate Payment",
                        "task_type": "payment_validation",
                        "config": {"amount": 100.00}
                    },
                    {
                        "name": "Process Payment",
                        "task_type": "payment_execution",
                        "config": {"gateway": "stripe"}
                    }
                ],
                "priority": 3,
                "tags": ["payment", "critical"]
            }
        }
    )


class JobUpdate(BaseModel):
    """Schema for updating a job."""
    state: Optional[JobState] = None
    priority: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[List[str]] = None


class JobResponse(BaseModel):
    """Schema for job API response."""
    id: int
    tenant_id: int
    name: str
    job_type: str
    state: JobState
    trigger_type: TriggerType
    
    config: dict
    max_retries: int
    retry_count: int
    retry_policy: str
    priority: int
    tags: List[str]
    
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    
    error_message: Optional[str] = None
    error_classification: Optional[str] = None
    
    # AI context (if applicable)
    agent_context: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    """Schema for paginated job list."""
    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int