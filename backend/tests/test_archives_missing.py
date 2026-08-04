import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from app.modules.payments.models import Order, OrderItem
from app.modules.downloads.models import DownloadPermission
from app.modules.competitions.models import Photo
from app.modules.archives.models import Archive, ArchiveStatus, ArchiveType
from datetime import datetime, timezone, timedelta

@pytest.mark.asyncio
async def test_create_archive_order_not_found(async_client, db_session):
    response = await async_client.post("/orders/999/archives")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_archive_no_permission(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    response = await async_client.post(f"/orders/{order.id}/archives")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_archive_success(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    perm = DownloadPermission(order_id=order.id, expires_at=datetime.now(timezone.utc) + timedelta(days=1))
    db_session.add(perm)
    await db_session.commit()
    
    photo = Photo(s3_object_key="originals/test.jpg", epreuve_id=1)
    db_session.add(photo)
    await db_session.commit()
    
    item = OrderItem(order_id=order.id, photo_id=photo.id, price=1000)
    db_session.add(item)
    await db_session.commit()
    
    class MockRedis:
        async def enqueue_job(self, *args, **kwargs):
            pass
            
    with patch("app.modules.archives.router.get_redis_pool", new_callable=AsyncMock) as mock_pool:
        mock_pool.return_value = MockRedis()
        response = await async_client.post(f"/orders/{order.id}/archives")
        assert response.status_code == 200
        assert "archive_id" in response.json()

@pytest.mark.asyncio
async def test_archive_callback(async_client, db_session):
    order = Order(user_id=1, total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    archive = Archive(order_id=order.id, archive_type=ArchiveType.ZIP, status=ArchiveStatus.PENDING)
    db_session.add(archive)
    await db_session.commit()
    
    response = await async_client.post(
        f"/orders/{order.id}/archives/{archive.id}/callback",
        json={"status": "COMPLETED", "s3_object_key": "zips/test.zip", "size": 1024}
    )
    assert response.status_code == 200
    
    await db_session.refresh(archive)
    assert archive.status == ArchiveStatus.COMPLETED
    assert archive.s3_object_key == "zips/test.zip"
