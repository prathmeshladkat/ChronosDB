"""Users model for saas authentication"""

from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from chronosdb.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from chronosdb.models.tenant import Tenant

class User(Base, TimestampMixin):
    """
    User within a tenant
    Future :  add authentication roles, permission
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    #Tenant Relationship
    tenant_id : Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    #Identification
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Auth (simplified for now)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # API key (for programmatic access)
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationship
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="users")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"
