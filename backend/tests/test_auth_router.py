import pytest
from unittest.mock import patch, AsyncMock
from app.modules.auth.models import User, PhotographerProfile

@pytest.mark.asyncio
async def test_request_otp(async_client):
    with patch("app.modules.auth.service.generate_and_send_otp", new_callable=AsyncMock) as mock_service:
        response = await async_client.post("/auth/request-otp", json={"phone_number": "+221770000000"})
        assert response.status_code == 200
        assert response.json() == {"message": "OTP sent successfully"}
        mock_service.assert_awaited_once()

@pytest.mark.asyncio
async def test_verify_otp_success(async_client):
    with patch("app.modules.auth.service.verify_otp_and_login", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = {"access_token": "fake_token", "token_type": "bearer"}
        
        response = await async_client.post("/auth/verify", json={"phone_number": "+221770000000", "code": "1234"})
        
        assert response.status_code == 200
        assert response.json() == {"access_token": "fake_token", "token_type": "bearer"}
        mock_verify.assert_awaited_once()

@pytest.mark.asyncio
async def test_verify_otp_with_session(async_client):
    with patch("app.modules.auth.service.verify_otp_and_login", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = {"access_token": "fake_token", "token_type": "bearer", "user_id": 99}
        
        with patch("app.modules.athletes.services.merge_guest_orders", new_callable=AsyncMock) as mock_merge:
            response = await async_client.post("/auth/verify", json={"phone_number": "+221770000000", "code": "1234"}, headers={"X-Session-ID": "guest123"})
            
            assert response.status_code == 200
            mock_verify.assert_awaited_once()
            mock_merge.assert_awaited_once_with(pytest.ANY, 99, "guest123")

@pytest.mark.asyncio
async def test_verify_otp_failure(async_client):
    with patch("app.modules.auth.service.verify_otp_and_login", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = None
        
        response = await async_client.post("/auth/verify", json={"phone_number": "+221770000000", "code": "0000"})
        
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_me(async_client, db_session):
    # Prepare User
    user = User(phone_number="+221771112233")
    db_session.add(user)
    await db_session.commit()
    
    from app.main import app
    from app.modules.auth.service import get_current_user
    
    app.dependency_overrides[get_current_user] = lambda: user
    
    response = await async_client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["phone_number"] == "+221771112233"
    assert data["photographer_profile"] is None
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_update_profile(async_client, db_session):
    user = User(phone_number="+221771112244")
    db_session.add(user)
    await db_session.commit()
    
    payload = {
        "full_name": "Test Photographe",
        "bio": "Je suis un test"
    }
    
    from app.main import app
    from app.modules.auth.service import get_current_user
    
    app.dependency_overrides[get_current_user] = lambda: user
    
    response = await async_client.put("/auth/me/profile", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Test Photographe"
    
    # Verify db
    await db_session.refresh(user)
    assert user.is_photographer is True
    
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_update_profile_existing(async_client, db_session):
    user = User(phone_number="+221771112255", is_photographer=True)
    db_session.add(user)
    await db_session.commit()
    
    profile = PhotographerProfile(user_id=user.id, full_name="Old Name", bio="Old Bio")
    db_session.add(profile)
    await db_session.commit()
    
    payload = {
        "full_name": "New Name",
        "bio": "New Bio"
    }
    
    from app.main import app
    from app.modules.auth.service import get_current_user
    
    app.dependency_overrides[get_current_user] = lambda: user
    
    response = await async_client.put("/auth/me/profile", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "New Name"
    assert data["bio"] == "New Bio"
    
    await db_session.refresh(profile)
    assert profile.full_name == "New Name"
    
    app.dependency_overrides.clear()
