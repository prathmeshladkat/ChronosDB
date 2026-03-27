"""FailurePattern model — stores historical failure data for AI learning."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from chronosdb.models.base import Base, TimestampMixin


class FailurePattern(Base, TimestampMixin):
    """
    Historical failure data for AI-powered retry learning.
    
    Tracks:
    - What error occurred
    - How it was classified (transient, permanent, etc.)
    - How many retries it took to recover
    - How long recovery took
    - Whether it eventually succeeded
    """
    __tablename__ = "failure_patterns"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Tenant scoping
    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Job/Step context
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False)
    step_id: Mapped[int] = mapped_column(Integer, ForeignKey("steps.id"), nullable=False)
    
    # Error details
    error_message: Mapped[str] = mapped_column(String, nullable=False)
    error_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # e.g., "NetworkTimeout", "AuthError", "RateLimitExceeded"
    
    error_classification: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # e.g., "transient", "permanent", "backpressure"
    
    # Retry metadata
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False)
    retry_policy_used: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Outcome
    eventually_succeeded: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_to_recovery_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # NULL if never recovered
    
    # Timing
    first_failure_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    final_outcome_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    def __repr__(self) -> str:
        return f"<FailurePattern(error_type='{self.error_type}', retries={self.retry_count}, succeeded={self.eventually_succeeded})>"