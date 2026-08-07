import pytest
from httpx import AsyncClient
from app.modules.auth.models import User, OTPCode, TokenBlacklist
from app.modules.competitions.models import Competition, Epreuve, PhotoStatus
from app.modules.subscriptions.models import StorageUsage
from app.core.security import create_access_token, create_refresh_token
from datetime import datetime, timedelta, timezone

@pytest.mark.asyncio
async def test_refresh_token_rotation(async_client: AsyncClient, db_session):
    # 1. Mock a user
    user = User(phone_number="+221770000000")
    db_session.add(user)
    await db_session.commit()
    
    # Generate tokens
    refresh_token = create_refresh_token(data={"sub": "+221770000000"})
    
    # 2. Call /refresh
    response = await async_client.post("/api/v1/auth/refresh", params={"refresh_token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
    new_refresh = data["refresh_token"]
    assert new_refresh != refresh_token
    
    # 3. Call /refresh again with the OLD token (should be blacklisted)
    response2 = await async_client.post("/api/v1/auth/refresh", params={"refresh_token": refresh_token})
    assert response2.status_code == 401
    
@pytest.mark.asyncio
async def test_quota_blocks_upload(async_client: AsyncClient, db_session):
    # Setup Competition and Epreuve
    user = User(phone_number="+221770000001", id=2)
    db_session.add(user)
    
    comp = Competition(id=1, name="Quota Test", photographer_id=2, date=datetime.now(timezone.utc))
    db_session.add(comp)
    
    ep = Epreuve(id=1, competition_id=1, name="Sprint")
    db_session.add(ep)
    
    # Add StorageUsage that is near limit (Limit is 1 Go = 1073741824 bytes)
    # We use 1073741824 - 100 bytes
    usage = StorageUsage(user_id=2, used_bytes=1073741724)
    db_session.add(usage)
    await db_session.commit()
    
    # Attempt to add photo (size 5 MB)
    token = create_access_token(data={"sub": "+221770000001"})
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await async_client.post(
        "/api/v1/competitions/epreuves/1/photos",
        json={"s3_object_key": "test_photo.jpg"}, # Will use fallback size 5 MB
        headers=headers
    )
    
    assert response.status_code == 413
    assert "limite de stockage" in response.json()["detail"]
