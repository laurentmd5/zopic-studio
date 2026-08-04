import pytest
from app.modules.subscriptions.service import (
    get_plans, get_user_subscription, create_subscription,
    get_storage_usage, add_storage_usage
)
from app.modules.subscriptions.models import Plan, Subscription, StorageUsage
from app.modules.auth.models import User
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_get_plans(db_session):
    plan = Plan(name="Basic", price_monthly=1000, storage_limit_gb=10, is_active=True)
    db_session.add(plan)
    await db_session.commit()
    
    plans = await get_plans(db_session)
    assert len(plans) >= 1

@pytest.mark.asyncio
async def test_get_user_subscription(db_session):
    user = User(phone_number="+221770000003")
    db_session.add(user)
    await db_session.commit()
    
    plan = Plan(name="Basic 2", price_monthly=1000, storage_limit_gb=10, is_active=True)
    db_session.add(plan)
    await db_session.commit()
    
    sub = Subscription(user_id=user.id, plan_id=plan.id, is_active=True, end_date=datetime.now(timezone.utc))
    db_session.add(sub)
    await db_session.commit()
    
    fetched = await get_user_subscription(db_session, user.id)
    assert fetched.id == sub.id

@pytest.mark.asyncio
async def test_create_subscription(db_session):
    user = User(phone_number="+221770000004")
    db_session.add(user)
    await db_session.commit()
    
    plan = Plan(name="Basic 3", price_monthly=1000, storage_limit_gb=10, is_active=True)
    db_session.add(plan)
    await db_session.commit()
    
    # Create first
    sub1 = await create_subscription(db_session, user.id, plan.id)
    assert sub1.plan_id == plan.id
    assert sub1.is_active is True
    
    # Create second, should deactivate first
    sub2 = await create_subscription(db_session, user.id, plan.id)
    
    await db_session.refresh(sub1)
    assert sub1.is_active is False
    assert sub2.is_active is True

@pytest.mark.asyncio
async def test_get_storage_usage_new(db_session):
    user = User(phone_number="+221770000005")
    db_session.add(user)
    await db_session.commit()
    
    usage = await get_storage_usage(db_session, user.id)
    assert usage.used_bytes == 0.0

@pytest.mark.asyncio
async def test_get_storage_usage_existing(db_session):
    user = User(phone_number="+221770000006")
    db_session.add(user)
    await db_session.commit()
    
    existing = StorageUsage(user_id=user.id, used_bytes=100.5)
    db_session.add(existing)
    await db_session.commit()
    
    usage = await get_storage_usage(db_session, user.id)
    assert usage.used_bytes == 100.5

@pytest.mark.asyncio
async def test_add_storage_usage(db_session):
    user = User(phone_number="+221770000007")
    db_session.add(user)
    await db_session.commit()
    
    usage = await add_storage_usage(db_session, user.id, 50.0)
    assert usage.used_bytes == 50.0
    
    usage2 = await add_storage_usage(db_session, user.id, 25.5)
    assert usage2.used_bytes == 75.5
