"""Pydantic schemas for Step API."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from chronosdb.config.constants import StepState, StepType


class StepCreate(BaseModel):
    """Schema for creating a step (usually embedded in JobCreate)."""
    name: str
    task_type: str
    step_type: StepType = StepType.TASK
    config: dict = {}
    max_retries: int = 3
    timeout_seconds: Optional[int] = None
    
    # AI-specific
    llm_config: Optional[dict] = None
    decision_logic: Optional[dict] = None


class StepResponse(BaseModel):
    """Schema for step API response."""
    id: int
    job_id: int
    name: str
    order: int
    state: StepState
    step_type: StepType
    task_type: str
    
    config: dict
    max_retries: int
    retry_count: int
    
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    result: Optional[dict] = None
    error_message: Optional[str] = None
    
    # AI fields
    llm_config: Optional[dict] = None
    decision_logic: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)