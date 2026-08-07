from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user
from app.modules.subscriptions import service, schemas

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.get("/plans", response_model=List[schemas.PlanResponse])
async def get_plans(db: AsyncSession = Depends(get_db)):
    return await service.get_plans(db)

@router.get("/me", response_model=schemas.SubscriptionResponse)
async def get_my_subscription(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    sub = await service.get_user_subscription(db, current_user.id)
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found")
    return sub

@router.post("/subscribe", response_model=schemas.SubscriptionResponse)
async def subscribe(data: schemas.SubscriptionCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # TODO: Intégration PayDunya pour les abonnements récurrents
    return await service.create_subscription(db, current_user.id, data.plan_id)

@router.get("/storage", response_model=schemas.StorageUsageResponse)
async def get_my_storage(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await service.get_storage_usage(db, current_user.id)
