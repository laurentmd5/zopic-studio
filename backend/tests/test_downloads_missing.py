import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.modules.payments.models import Order, OrderItem
from app.modules.downloads.models import DownloadPermission
from app.modules.competitions.models import Photo
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user_optional
from app.main import app
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_download_photo_order_not_found(async_client, db_session):
    response = await async_client.get("/api/v1/orders/999/photos/1/download")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_download_photo_session_mismatch(async_client, db_session):
    order = Order(user_id=1, total_amount=1000, session_id="sess_123")
    db_session.add(order)
    await db_session.commit()
    
    response = await async_client.get(
        f"/api/v1/orders/{order.id}/photos/1/download",
        headers={"x-session-id": "sess_456"}
    )
    assert response.status_code == 403
    assert "Accès non autorisé" in response.json()["detail"]

@pytest.mark.asyncio
async def test_download_photo_not_in_order(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    user = User(id=1, phone_number="1234")
    app.dependency_overrides[get_current_user_optional] = lambda: user
    
    response = await async_client.get(f"/api/v1/orders/{order.id}/photos/1/download")
    app.dependency_overrides.clear()
    assert response.status_code == 403
    assert "n'appartient pas" in response.json()["detail"]

@pytest.mark.asyncio
async def test_download_photo_no_permission(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    item = OrderItem(order_id=order.id, photo_id=1, price=1000)
    db_session.add(item)
    await db_session.commit()
    
    user = User(id=1, phone_number="1234")
    app.dependency_overrides[get_current_user_optional] = lambda: user

    response = await async_client.get(f"/api/v1/orders/{order.id}/photos/1/download")
    app.dependency_overrides.clear()
    assert response.status_code == 403
    assert "Aucun droit" in response.json()["detail"]

@pytest.mark.asyncio
async def test_download_photo_expired_permission(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    item = OrderItem(order_id=order.id, photo_id=1, price=1000)
    db_session.add(item)
    await db_session.commit()
    
    perm = DownloadPermission(order_id=order.id, expires_at=datetime.now(timezone.utc) - timedelta(days=1))
    db_session.add(perm)
    await db_session.commit()
    
    user = User(id=1, phone_number="1234")
    app.dependency_overrides[get_current_user_optional] = lambda: user

    response = await async_client.get(f"/api/v1/orders/{order.id}/photos/1/download")
    app.dependency_overrides.clear()
    assert response.status_code == 403
    assert "expiré" in response.json()["detail"]

@pytest.mark.asyncio
async def test_download_photo_success(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    photo = Photo(s3_object_key="originals/test.jpg", epreuve_id=1)
    db_session.add(photo)
    await db_session.commit()
    
    item = OrderItem(order_id=order.id, photo_id=photo.id, price=1000)
    db_session.add(item)
    await db_session.commit()
    
    perm = DownloadPermission(order_id=order.id, expires_at=datetime.now(timezone.utc) + timedelta(days=1))
    db_session.add(perm)
    await db_session.commit()
    
    user = User(id=1, phone_number="1234")
    app.dependency_overrides[get_current_user_optional] = lambda: user

    with patch("app.modules.downloads.router.generate_download_url", new_callable=AsyncMock) as mock_url:
        mock_url.return_value = "http://download.url"
        response = await async_client.get(f"/api/v1/orders/{order.id}/photos/{photo.id}/download")
        
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["download_url"] == "http://download.url"
