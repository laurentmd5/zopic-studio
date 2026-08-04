import pytest
from unittest.mock import patch, AsyncMock
from app.modules.auth.models import User
from app.modules.subscriptions.models import Plan, Subscription

@pytest.mark.asyncio
async def test_get_plans(async_client, db_session):
    plan = Plan(name="Pro", storage_limit_gb=50, price_monthly=10000)
    db_session.add(plan)
    await db_session.commit()
    
    response = await async_client.get("/subscriptions/plans")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["name"] == "Pro"

@pytest.mark.asyncio
async def test_get_my_subscription(async_client, db_session):
    user = User(phone_number="+221770000000")
    db_session.add(user)
    await db_session.commit()
    
    plan = Plan(name="Basic", storage_limit_gb=5, price_monthly=0)
    db_session.add(plan)
    await db_session.commit()
    
    from datetime import datetime, timedelta, timezone
    sub = Subscription(user_id=user.id, plan_id=plan.id, end_date=datetime.now(timezone.utc) + timedelta(days=30))
    db_session.add(sub)
    await db_session.commit()
    
    from app.main import app
    from app.modules.auth.service import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user
    
    response = await async_client.get("/subscriptions/me")
    assert response.status_code == 200
    assert response.json()["plan_id"] == plan.id
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_subscribe(async_client, db_session):
    user = User(phone_number="+221770000000")
    db_session.add(user)
    await db_session.commit()
    
    plan = Plan(name="Pro", storage_limit_gb=50, price_monthly=10000)
    db_session.add(plan)
    await db_session.commit()
    
    from app.main import app
    from app.modules.auth.service import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user
    
    response = await async_client.post("/subscriptions/subscribe", json={"plan_id": plan.id})
    assert response.status_code == 200
    assert response.json()["plan_id"] == plan.id
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_storage_usage(async_client, db_session):
    user = User(phone_number="+221770000000")
    db_session.add(user)
    await db_session.commit()
    
    from app.main import app
    from app.modules.auth.service import get_current_user
    app.dependency_overrides[get_current_user] = lambda: user
    
    from app.modules.subscriptions.models import StorageUsage
    from datetime import datetime
    mock_usage = StorageUsage(id=1, user_id=user.id, used_bytes=1000, updated_at=datetime.now())
    
    with patch("app.modules.subscriptions.service.get_storage_usage", new_callable=AsyncMock) as mock_srv:
        mock_srv.return_value = mock_usage
        response = await async_client.get("/subscriptions/storage")
        assert response.status_code == 200
        assert response.json()["used_bytes"] == 1000
    app.dependency_overrides.clear()
