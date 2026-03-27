"""Organization model for Saas multi-tenancy"""

from typing import Optional, TYPE_CHECKING, List
from sqlalchemy import String, Boolean, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from chronosdb.models.base import Base, TimestampMixin 

if TYPE_CHECKING:
    from chronosdb.models.user import User
    from chronosdb.models.job import Job

class Tenant(Base, TimestampMixin):
    """
    organization for SaaS multi-tenancy

    Each tenant has :
    -Isolated data(jobs steps, execution)
    -own users and api keys
    -Billing subscription info
    """

    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    #Identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    #Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    #Limits(for SaaS tier)
    max_jobs_per_month : Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_concurrent_jobs : Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    #Feature flags
    features : Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Example: {"ai_retry_policies": true, "webhooks": true, "priority_queue": false}


    #Billing metadata 
    subscription_tier : Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    billing_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    #Relationships
    users: Mapped[List["User"]] =  relationship("User", back_populates="tenant")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="tenant")

    def __repr__(self) -> str:
        return f"<Tenant(id={self.id}, slug='{self.slug}', name='{self.name}')>"