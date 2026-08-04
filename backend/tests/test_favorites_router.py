import pytest
from unittest.mock import patch
from app.modules.competitions.models import Favorite
from app.modules.auth.models import User
from app.modules.competitions.models import Photo, Epreuve, Competition

@pytest.mark.asyncio
async def test_add_favorite_guest(async_client, db_session):
    # Setup
    from datetime import datetime, timezone
    comp = Competition(name="Fav Event", date=datetime.now(timezone.utc), photographer_id=1)
    db_session.add(comp)
    await db_session.commit()
    ep = Epreuve(name="E1", competition_id=comp.id)
    db_session.add(ep)
    await db_session.commit()
    photo = Photo(epreuve_id=ep.id, s3_object_key="test_fav.jpg")
    db_session.add(photo)
    await db_session.commit()
    
    response = await async_client.post(
        f"/api/v1/favorites/{photo.id}", 
        headers={"x-session-id": "guest_123"}
    )
    
    assert response.status_code == 201
    assert response.json()["photo_id"] == photo.id

@pytest.mark.asyncio
async def test_list_favorites_guest(async_client, db_session):
    response = await async_client.get("/api/v1/favorites/", headers={"x-session-id": "guest_123"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_remove_favorite_guest(async_client, db_session):
    # Require adding it first
    from datetime import datetime, timezone
    comp = Competition(name="Fav Event", date=datetime.now(timezone.utc), photographer_id=1)
    db_session.add(comp)
    await db_session.commit()
    ep = Epreuve(name="E1", competition_id=comp.id)
    db_session.add(ep)
    await db_session.commit()
    photo = Photo(epreuve_id=ep.id, s3_object_key="test_fav_rem.jpg")
    db_session.add(photo)
    await db_session.commit()
    
    fav = Favorite(session_id="guest_123", photo_id=photo.id)
    db_session.add(fav)
    await db_session.commit()
    
    response = await async_client.delete(f"/api/v1/favorites/{photo.id}", headers={"x-session-id": "guest_123"})
    
    assert response.status_code == 204
