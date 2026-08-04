import pytest
from unittest.mock import patch, AsyncMock
from app.modules.payments.models import Order, OrderStatus, OrderItem, PhotoSale
from app.modules.archives.models import Archive, ArchiveStatus
from app.modules.downloads.models import DownloadPermission
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user_optional
from app.modules.competitions.models import Photo, Epreuve, Competition
from app.modules.payments.service import create_order, process_webhook
from app.modules.payments.schemas import OrderCreate
from fastapi import HTTPException
from datetime import datetime, timezone
from app.main import app

@pytest.mark.asyncio
async def test_get_purchases_missing_auth(async_client):
    response = await async_client.get("/payments/purchases")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_get_purchases_user(async_client, db_session):
    user = User(phone_number="+221770000008")
    db_session.add(user)
    await db_session.commit()
    
    order = Order(user_id=user.id, total_amount=1000, status=OrderStatus.PAID)
    db_session.add(order)
    await db_session.commit()
    
    app.dependency_overrides[get_current_user_optional] = lambda: user
    
    response = await async_client.get("/payments/purchases")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_purchases_guest(async_client, db_session):
    app.dependency_overrides[get_current_user_optional] = lambda: None
    
    order = Order(session_id="sess_5", total_amount=1000, status=OrderStatus.PAID)
    db_session.add(order)
    await db_session.commit()
    
    item = OrderItem(order_id=order.id, photo_id=1, price=1000)
    db_session.add(item)
    await db_session.commit()
    
    perm = DownloadPermission(order_id=order.id, expires_at=datetime.now(timezone.utc))
    db_session.add(perm)
    await db_session.commit()
    
    arch = Archive(order_id=order.id, status=ArchiveStatus.COMPLETED)
    db_session.add(arch)
    await db_session.commit()
    
    response = await async_client.get("/payments/purchases", headers={"x-session-id": "sess_5"})
    assert response.status_code == 200
    assert len(response.json()) >= 1
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_webhook_paydunya_missing_token(async_client):
    response = await async_client.post("/payments/webhook/paydunya", json={"data": {"status": "completed"}})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_webhook_paydunya_valid(async_client, db_session):
    with patch("app.modules.payments.service.process_webhook", new_callable=AsyncMock) as mock_pw:
        mock_pw.return_value = {"status": "ok"}
        response = await async_client.post("/payments/webhook/paydunya", json={"data": {"status": "completed", "token": "tok_123"}})
        assert response.status_code == 200
        mock_pw.assert_called_once()

@pytest.mark.asyncio
async def test_create_order_fallback_price_and_mismatch(db_session):
    comp = Competition(name="Comp", date=datetime.now(timezone.utc), photographer_id=1, packs_enabled=False)
    db_session.add(comp)
    await db_session.commit()
    
    ep = Epreuve(name="Ep", competition_id=comp.id)
    db_session.add(ep)
    await db_session.commit()
    
    photo = Photo(s3_object_key="key2", epreuve_id=ep.id)
    db_session.add(photo)
    await db_session.commit()
    
    with pytest.raises(HTTPException) as exc:
        await create_order(db_session, OrderCreate(photo_ids=[photo.id], amount_expected=1000, return_url="url", cancel_url="url"), None, None)
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_process_webhook_success_ledger(db_session):
    comp = Competition(name="Comp", date=datetime.now(timezone.utc), photographer_id=1)
    db_session.add(comp)
    await db_session.commit()
    
    ep = Epreuve(name="Ep", competition_id=comp.id)
    db_session.add(ep)
    await db_session.commit()
    
    photo = Photo(s3_object_key="key3", epreuve_id=ep.id)
    db_session.add(photo)
    await db_session.commit()
    
    order = Order(total_amount=1500, status=OrderStatus.PENDING, paydunya_token="token_C")
    db_session.add(order)
    await db_session.commit()
    
    item = OrderItem(order_id=order.id, photo_id=photo.id, price=1500)
    db_session.add(item)
    await db_session.commit()
    
    with patch("app.core.events.event_bus.publish", new_callable=AsyncMock):
        res = await process_webhook(db_session, "token_C", True)
        assert res["status"] == "paid_recorded_and_ledger_created"
        
        await db_session.refresh(order)
        assert order.status == OrderStatus.PAID
