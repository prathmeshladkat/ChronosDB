from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from chronosdb.api.dependencies import get_db
from chronosdb.services.tenant_service import TenantService
from chronosdb.schemas.tenant import TenantCreate, TenantResponse

#Create Router
#To group related endponits together
router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tenant"
)
async def create_tenant(
    data: TenantCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new tenant.

    Example request:
```
    POST /tenants
    {
        "name": "Acme Corp",
        "slug": "acme",
        "max_concurrent_jobs": 50
    }
```
    
    Returns created tenant with ID.
    """
    service = TenantService(db)

    try:
        tenant = await service.create_tenant(data)
        return tenant
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    

    
@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Get tenant by ID"
)
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get tenant details.
    
    Example:
```
    GET /tenants/1
```
    """
    service = TenantService(db)
    tenant = await service.get_tenant(tenant_id)
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} not found"
        )
    
    return tenant