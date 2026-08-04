import pytest
from unittest.mock import patch, AsyncMock
from app.modules.payments.models import Order, OrderItem
from app.modules.competitions.models import Photo, Competition, Epreuve
from app.modules.downloads.models import DownloadPermission
from datetime import datetime, timedelta, timezone

@pytest.mark.asyncio
async def test_download_photo_success(async_client, db_session):
    # Setup Data
    comp = Competition(name="Ev", date=datetime.now(timezone.utc), photographer_id=1)
    db_session.add(comp)
    await db_session.commit()
    ep = Epreuve(name="E1", competition_id=comp.id)
    db_session.add(ep)
    await db_session.commit()
    photo = Photo(epreuve_id=ep.id, s3_object_key="test_obj.jpg")
    db_session.add(photo)
    await db_session.commit()
    
    order = Order(session_id="sess_1", total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    item = OrderItem(order_id=order.id, photo_id=photo.id, price=1000)
    db_session.add(item)
    
    perm = DownloadPermission(
        order_id=order.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1)
    )
    db_session.add(perm)
    await db_session.commit()
    
    with patch("app.modules.downloads.router.generate_download_url", new_callable=AsyncMock) as mock_url:
        mock_url.return_value = "http://presigned.url"
        
        res = await async_client.get(
            f"/orders/{order.id}/photos/{photo.id}/download",
            headers={"x-session-id": "sess_1"}
        )
        
        assert res.status_code == 200
        assert res.json()["download_url"] == "http://presigned.url"

@pytest.mark.asyncio
async def test_download_photo_no_permission(async_client, db_session):
    # Setup Data
    order = Order(session_id="sess_2", total_amount=1000)
    db_session.add(order)
    await db_session.commit()
    
    photo = Photo(epreuve_id=1, s3_object_key="test_obj_2.jpg")
    db_session.add(photo)
    await db_session.commit()
    
    item = OrderItem(order_id=order.id, photo_id=photo.id, price=1000)
    db_session.add(item)
    await db_session.commit()
    
    res = await async_client.get(
        f"/orders/{order.id}/photos/{photo.id}/download",
        headers={"x-session-id": "sess_2"}
    )
    
    assert res.status_code == 403
    assert "Aucun droit de téléchargement" in res.json()["detail"]
