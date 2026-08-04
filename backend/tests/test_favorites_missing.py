import pytest
from app.modules.auth.models import User
from app.modules.competitions.models import Photo, Favorite
from app.modules.auth.service import get_current_user_optional
from app.main import app

@pytest.mark.asyncio
async def test_add_favorite_missing_auth(async_client):
    response = await async_client.post("/api/v1/favorites/1")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_add_favorite_photo_not_found(async_client):
    user = User(id=1, phone_number="+221770000001")
    app.dependency_overrides[get_current_user_optional] = lambda: user
    
    response = await async_client.post("/api/v1/favorites/999")
    assert response.status_code == 404
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_add_favorite_success_user(async_client, db_session):
    user = User(phone_number="+221770000002")
    db_session.add(user)
    await db_session.commit()
    
    photo = Photo(s3_object_key="key", epreuve_id=1)
    db_session.add(photo)
    await db_session.commit()
    
    app.dependency_overrides[get_current_user_optional] = lambda: user
    
    response = await async_client.post(f"/api/v1/favorites/{photo.id}")
    assert response.status_code == 201
    
    response2 = await async_client.post(f"/api/v1/favorites/{photo.id}")
    assert response2.status_code == 201
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_add_favorite_success_guest(async_client, db_session):
    app.dependency_overrides[get_current_user_optional] = lambda: None
    
    photo = Photo(s3_object_key="key2", epreuve_id=1)
    db_session.add(photo)
    await db_session.commit()
    
    response = await async_client.post(f"/api/v1/favorites/{photo.id}", headers={"x-session-id": "sess_1"})
    assert response.status_code == 201
    
    response2 = await async_client.post(f"/api/v1/favorites/{photo.id}", headers={"x-session-id": "sess_1"})
    assert response2.status_code == 201
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_remove_favorite_missing_auth(async_client):
    response = await async_client.delete("/api/v1/favorites/1")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_remove_favorite_not_found(async_client):
    user = User(id=1, phone_number="+221770000003")
    app.dependency_overrides[get_current_user_optional] = lambda: user
    
    response = await async_client.delete("/api/v1/favorites/999")
    assert response.status_code == 404
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_remove_favorite_success_user(async_client, db_session):
    user = User(phone_number="+221770000004")
    db_session.add(user)
    await db_session.commit()
    
    fav = Favorite(photo_id=1, user_id=user.id)
    db_session.add(fav)
    await db_session.commit()
    
    app.dependency_overrides[get_current_user_optional] = lambda: user
    
    response = await async_client.delete(f"/api/v1/favorites/1")
    assert response.status_code == 204
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_remove_favorite_success_guest(async_client, db_session):
    app.dependency_overrides[get_current_user_optional] = lambda: None
    
    fav = Favorite(photo_id=1, session_id="sess_2")
    db_session.add(fav)
    await db_session.commit()
    
    response = await async_client.delete(f"/api/v1/favorites/1", headers={"x-session-id": "sess_2"})
    assert response.status_code == 204
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_favorites_missing_auth(async_client):
    response = await async_client.get("/api/v1/favorites/")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_get_favorites_user(async_client, db_session):
    user = User(phone_number="+221770000005")
    db_session.add(user)
    await db_session.commit()
    
    fav = Favorite(photo_id=1, user_id=user.id)
    db_session.add(fav)
    await db_session.commit()
    
    app.dependency_overrides[get_current_user_optional] = lambda: user
    
    response = await async_client.get("/api/v1/favorites/")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_favorites_guest(async_client, db_session):
    app.dependency_overrides[get_current_user_optional] = lambda: None
    
    fav = Favorite(photo_id=1, session_id="sess_3")
    db_session.add(fav)
    await db_session.commit()
    
    response = await async_client.get("/api/v1/favorites/", headers={"x-session-id": "sess_3"})
    assert response.status_code == 200
    assert len(response.json()) >= 1
    app.dependency_overrides.clear()
