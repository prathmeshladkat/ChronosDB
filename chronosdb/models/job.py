""""Job model - represents a background job/workflow"""
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import String, Enum as SQLEnum, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from chronosdb.config.constants import JobState, TriggerType
from chronosdb.models.base import TimestampMixin, Base

if TYPE_CHECKING:
    from chronosdb.models.tenant import Tenant
    from chronosdb.models.step import Step

class Job(Base, TimestampMixin):
    """
    Job epresents a background task/workflow

    A job consits of multiple steps executed sequentiall.
    can  be triggered by human schedules webhoooks
    """
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    #Multi- tenancy
    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    #ownership (who created a job)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # job identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    #state
    state: Mapped[JobState] = mapped_column(
        SQLEnum(JobState, native_enum=False),
        default=TriggerType.PENDING,
        nullable=False,
        index=True
    )

    #Trigger information (human vs AI agent)
    trigger_type: Mapped[TriggerType] = mapped_column(
        SQLEnum(TriggerType, native_enum=False),
        default=TriggerType.MANUAL,
        nullable=False,
        index=True
    )

    #AI agent context 
    agent_context : Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Example: {
    #   "agent_id": "gpt-4-agent-001",
    #   "reasoning": "User requested payment retry due to network issue",
    #   "confidence": 0.95,
    #   "prompt": "...",
    #   "model": "gpt-4"
    # }

     # Configuration
    config: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    
    # Retry configuration
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # 🔌 Retry policy (pluggable)
    retry_policy: Mapped[str] = mapped_column(
        String(100),
        default="exponential_backoff",
        nullable=False
    )
    # Future: "ai_intelligent_retry", "adaptive_backoff", "cost_optimized"
    
    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_classification: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Future AI: "transient_network", "auth_failure", "rate_limit", "data_validation"
    
    # Priority (for future SaaS tiering)
    priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False, index=True)
    # 1 = highest, 10 = lowest
    
    # Tags (for filtering/organization)
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="jobs")
    steps: Mapped[List["Step"]] = relationship(
        "Step",
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="Step.order"
    )
    
    def __repr__(self) -> str:
        return f"<Job(id={self.id}, tenant_id={self.tenant_id}, name='{self.name}', state={self.state.value})>"
