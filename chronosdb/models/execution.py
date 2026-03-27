"""Execution model - tracks individual step execution attempts"""
"""Execution model — tracks individual step execution attempts."""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Enum as SQLEnum, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from chronosdb.config.constants import ExecutionStatus
from chronosdb.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from chronosdb.models.step import Step


class Execution(Base, TimestampMixin):
    """
    Execution tracks a single attempt to execute a Step.
    
    Why separate from Step?
    - Step can be retried multiple times
    - Each retry creates a new Execution record
    - Provides full audit trail
    - Enables idempotency checking
    """
    __tablename__ = "executions"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to Step
    step_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("steps.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Idempotency key (unique per step + attempt)
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Execution metadata
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[ExecutionStatus] = mapped_column(
        SQLEnum(ExecutionStatus, native_enum=False),
        nullable=False,
        index=True
    )
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Result
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationship
    step: Mapped["Step"] = relationship("Step", back_populates="executions")
    
    def __repr__(self) -> str:
        return f"<Execution(id={self.id}, step_id={self.step_id}, attempt={self.attempt_number}, status={self.status.value})>"