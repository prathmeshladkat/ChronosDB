"""
Seed database with sample data for development/testing.

Usage:
    python -m chronosdb.db.seed
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from chronosdb.db.session import AsyncSessionLocal
from chronosdb.models.tenant import Tenant
from chronosdb.models.user import User
from chronosdb.models.job import Job
from chronosdb.models.step import Step
from chronosdb.config.constants import JobState, StepState, TriggerType, StepType


async def seed_data():
    """Seed database with sample tenants, users, and jobs."""
    async with AsyncSessionLocal() as db:
        # Create tenants
        tenant1 = Tenant(
            name="Acme Corporation",
            slug="acme",
            is_active=True,
            max_concurrent_jobs=100,
            features={"ai_retry": False},
        )
        tenant2 = Tenant(
            name="TechStart Inc",
            slug="techstart",
            is_active=True,
            max_concurrent_jobs=50,
            features={"ai_retry": False},
        )
        
        db.add_all([tenant1, tenant2])
        await db.commit()
        await db.refresh(tenant1)
        await db.refresh(tenant2)
        
        print(f"✅ Created tenant: {tenant1.name} (ID: {tenant1.id})")
        print(f"✅ Created tenant: {tenant2.name} (ID: {tenant2.id})")
        
        # Create users (optional for now)
        user1 = User(
            tenant_id=tenant1.id,
            email="admin@acme.com",
            name="Acme Admin",
            is_active=True,
        )
        
        db.add(user1)
        await db.commit()
        await db.refresh(user1)
        
        print(f"✅ Created user: {user1.email} (ID: {user1.id})")
        
        # Create sample job
        job1 = Job(
            tenant_id=tenant1.id,
            name="Sample Payment Processing",
            job_type="payment",
            state=JobState.PENDING,
            trigger_type=TriggerType.MANUAL,
            config={"customer_id": "cust_123", "amount": 100.00},
            max_retries=3,
            priority=5,
            tags=["payment", "sample"],
        )
        
        db.add(job1)
        await db.commit()
        await db.refresh(job1)
        
        print(f"✅ Created job: {job1.name} (ID: {job1.id})")
        
        # Create steps for job
        step1 = Step(
            job_id=job1.id,
            name="Validate Payment",
            order=0,
            state=StepState.PENDING,
            step_type=StepType.TASK,
            task_type="payment_validation",
            config={"checks": ["amount", "card", "cvv"]},
        )
        step2 = Step(
            job_id=job1.id,
            name="Process Payment",
            order=1,
            state=StepState.PENDING,
            step_type=StepType.TASK,
            task_type="payment_execution",
            config={"gateway": "stripe"},
        )
        step3 = Step(
            job_id=job1.id,
            name="Send Receipt",
            order=2,
            state=StepState.PENDING,
            step_type=StepType.TASK,
            task_type="email_notification",
            config={"template": "receipt"},
        )
        
        db.add_all([step1, step2, step3])
        await db.commit()
        
        print(f"✅ Created {3} steps for job {job1.id}")
        
        print("\n" + "=" * 60)
        print("🎉 Database seeded successfully!")
        print("=" * 60)
        print(f"\nTry:")
        print(f"  curl http://localhost:8000/api/v1/tenants/1")
        print(f"  curl http://localhost:8000/api/v1/jobs/1 -H 'X-Tenant-Id: 1'")


if __name__ == "__main__":
    asyncio.run(seed_data())