from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.subscriptions.models import Plan, Subscription, StorageUsage
from app.modules.subscriptions import schemas
from datetime import datetime, timedelta, timezone

async def get_plans(db: AsyncSession):
    result = await db.execute(select(Plan).where(Plan.is_active == True))
    return result.scalars().all()

async def get_user_subscription(db: AsyncSession, user_id: int):
    result = await db.execute(select(Subscription).where(Subscription.user_id == user_id, Subscription.is_active == True))
    return result.scalars().first()

async def create_subscription(db: AsyncSession, user_id: int, plan_id: int) -> Subscription:
    # On désactive l'ancien abonnement si présent
    existing = await get_user_subscription(db, user_id)
    if existing:
        existing.is_active = False
        
    subscription = Subscription(
        user_id=user_id,
        plan_id=plan_id,
        end_date=datetime.now(timezone.utc) + timedelta(days=30)
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    return subscription

async def get_storage_usage(db: AsyncSession, user_id: int) -> StorageUsage:
    result = await db.execute(select(StorageUsage).where(StorageUsage.user_id == user_id))
    usage = result.scalars().first()
    if not usage:
        usage = StorageUsage(user_id=user_id, used_bytes=0.0)
        db.add(usage)
        await db.commit()
        await db.refresh(usage)
    return usage

async def add_storage_usage(db: AsyncSession, user_id: int, bytes_added: float):
    usage = await get_storage_usage(db, user_id)
    usage.used_bytes += bytes_added
    await db.commit()
    return usage
