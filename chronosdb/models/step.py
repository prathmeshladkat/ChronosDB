"""Step model - represents a single step in a job """
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Enum as SQLEnum, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from chronosdb.config.constants import StepState, StepType
from chronosdb.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from chronosdb.models.job import Job
    from chronosdb.models.execution import Execution

class Step(Base, TimestampMixin):
    """
    Step represents a single unit of work in a job.

    Steps can be:
    -Regular task
    -LLM API calls
    -AI decision nodes
    """
    __tablename__ = "steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    #Foreign key to job
    job_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    #step identification 
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # State
    state: Mapped[StepState] = mapped_column(
        SQLEnum(StepState, native_enum=False),
        default=StepState.PENDING,
        nullable=False,
        index=True
    )
    
    # 🤖 Step type (extensible for AI features)
    step_type: Mapped[StepType] = mapped_column(
        SQLEnum(StepType, native_enum=False),
        default=StepType.TASK,
        nullable=False,
        index=True
    )
    
    # Task configuration
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    # 🧠 AI-specific fields (for LLM_CALL or DECISION steps)
    llm_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Example: {
    #   "model": "gpt-4",
    #   "temperature": 0.7,
    #   "prompt_template": "...",
    #   "max_tokens": 1000
    # }
    
    # Decision logic (for AI routing)
    decision_logic: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Example: {
    #   "on_success": "next_step",
    #   "on_failure": "fallback_step",
    #   "conditions": [...]
    # }
    
    # Retry configuration
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Timeout (for long-running AI calls)
    timeout_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Result storage
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="steps")
    executions: Mapped[List["Execution"]] = relationship(
        "Execution",
        back_populates="step",
        cascade="all, delete-orphan",
        order_by="Execution.created_at"
    )
    
    def __repr__(self) -> str:
        return f"<Step(id={self.id}, name='{self.name}', type={self.step_type.value}, state={self.state.value})>"