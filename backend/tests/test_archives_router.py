import pytest
from httpx import AsyncClient
from app.modules.archives.models import Archive, ArchiveStatus, ArchiveType
from app.modules.payments.models import Order, OrderItem
from app.modules.competitions.models import Photo
from app.modules.downloads.models import DownloadPermission
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_create_archive_no_order(async_client, db_session):
    response = await async_client.post("/api/v1/orders/999/archives")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_archive_no_permission(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    response = await async_client.post(f"/api/v1/orders/{order.id}/archives")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_archive_expired_permission(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    perm = DownloadPermission(order_id=order.id, expires_at=datetime.now(timezone.utc) - timedelta(days=1))
    db_session.add(perm)
    await db_session.commit()
    
    response = await async_client.post(f"/api/v1/orders/{order.id}/archives")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_archive_existing_processing(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    perm = DownloadPermission(order_id=order.id, expires_at=datetime.now(timezone.utc) + timedelta(days=1))
    db_session.add(perm)
    
    archive = Archive(order_id=order.id, archive_type=ArchiveType.ZIP, status=ArchiveStatus.PROCESSING)
    db_session.add(archive)
    await db_session.commit()
    
    response = await async_client.post(f"/api/v1/orders/{order.id}/archives")
    assert response.status_code == 200
    assert response.json()["status"] == "PROCESSING"

@pytest.mark.asyncio
async def test_create_archive_new(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    perm = DownloadPermission(order_id=order.id, expires_at=datetime.now(timezone.utc) + timedelta(days=1))
    db_session.add(perm)
    
    photo = Photo(s3_object_key="originals/test.jpg", epreuve_id=1)
    db_session.add(photo)
    await db_session.commit()
    
    item = OrderItem(order_id=order.id, photo_id=photo.id, price=1000)
    db_session.add(item)
    await db_session.commit()
    
    with patch("app.modules.archives.router.get_redis_pool", new_callable=AsyncMock) as mock_pool:
        mock_redis = AsyncMock()
        mock_pool.return_value = mock_redis
        
        response = await async_client.post(f"/api/v1/orders/{order.id}/archives")
        assert response.status_code == 200
        assert response.json()["status"] == "PROCESSING"
        mock_redis.enqueue_job.assert_called_once()

@pytest.mark.asyncio
async def test_create_archive_recreate_failed(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    perm = DownloadPermission(order_id=order.id, expires_at=datetime.now(timezone.utc) + timedelta(days=1))
    db_session.add(perm)
    
    archive = Archive(order_id=order.id, archive_type=ArchiveType.ZIP, status=ArchiveStatus.FAILED)
    db_session.add(archive)
    await db_session.commit()
    
    with patch("app.modules.archives.router.get_redis_pool", new_callable=AsyncMock) as mock_pool:
        mock_redis = AsyncMock()
        mock_pool.return_value = mock_redis
        
        response = await async_client.post(f"/api/v1/orders/{order.id}/archives")
        assert response.status_code == 200
        mock_redis.enqueue_job.assert_called_once()

@pytest.mark.asyncio
async def test_archive_callback_not_found(async_client):
    from app.core.config import settings
    response = await async_client.post(f"/api/v1/orders/1/archives/999/callback?secret={settings.SECRET_KEY}", json={"status": "COMPLETED"})
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_archive_callback_success(async_client, db_session):
    archive = Archive(order_id=1, archive_type=ArchiveType.ZIP, status=ArchiveStatus.PROCESSING)
    db_session.add(archive)
    await db_session.commit()
    
    from app.core.config import settings
    response = await async_client.post(
        f"/api/v1/orders/1/archives/{archive.id}/callback?secret={settings.SECRET_KEY}", 
        json={"status": "COMPLETED", "s3_object_key": "new.zip", "size": 2048}
    )
    assert response.status_code == 200
    
    await db_session.refresh(archive)
    assert archive.status == ArchiveStatus.COMPLETED
    assert archive.s3_object_key == "new.zip"
    assert archive.size == 2048


