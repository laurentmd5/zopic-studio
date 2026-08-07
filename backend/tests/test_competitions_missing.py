import pytest
from app.modules.auth.models import User
from app.modules.competitions.models import Competition, Epreuve
from app.modules.auth.service import get_current_user
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock
from app.main import app

@pytest.mark.asyncio
async def test_read_event_private_wrong_code(async_client, db_session):
    comp = Competition(name="Priv", date=datetime.now(timezone.utc), photographer_id=1, is_public=False, access_code="SECRET")
    db_session.add(comp)
    await db_session.commit()
    
    response = await async_client.get(f"/api/v1/competitions/{comp.id}?access_code=WRONG")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_packs_not_authorized(async_client, db_session):
    user1 = User(phone_number="+221771111113", is_photographer=True)
    user2 = User(phone_number="+221771111114", is_photographer=True)
    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()
    
    comp = Competition(name="Comp", date=datetime.now(timezone.utc), photographer_id=user1.id, is_public=True)
    db_session.add(comp)
    await db_session.commit()
    
    app.dependency_overrides[get_current_user] = lambda: user2
    
    response = await async_client.put(f"/api/v1/competitions/{comp.id}/packs", json={
        "packs_enabled": True, "packs": []
    })
    assert response.status_code == 403
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_update_packs_success(async_client, db_session):
    user = User(phone_number="+221771111115", is_photographer=True)
    db_session.add(user)
    await db_session.commit()
    
    comp = Competition(name="Comp", date=datetime.now(timezone.utc), photographer_id=user.id, is_public=True)
    db_session.add(comp)
    await db_session.commit()
    
    app.dependency_overrides[get_current_user] = lambda: user
    
    response = await async_client.put(f"/api/v1/competitions/{comp.id}/packs", json={
        "packs_enabled": True, 
        "packs": [{"label": "Pack1", "price_xof": 1000, "quantity": 5}]
    })
    assert response.status_code == 200
    assert response.json()["packs_enabled"] is True
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_packs_success(async_client, db_session):
    comp = Competition(name="Comp", date=datetime.now(timezone.utc), photographer_id=1, is_public=True, packs_enabled=True, packs=[{"label": "Pack1", "price_xof": 1000, "quantity": 5}])
    db_session.add(comp)
    await db_session.commit()
    
    response = await async_client.get(f"/api/v1/competitions/{comp.id}/packs")
    assert response.status_code == 200
    assert response.json()["packs_enabled"] is True
