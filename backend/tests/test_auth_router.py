import unittest
import pytest
from unittest.mock import patch, AsyncMock
from app.modules.auth.models import User, PhotographerProfile

@pytest.mark.asyncio
async def test_request_otp(async_client):
    with patch("app.modules.auth.service.generate_and_send_otp", new_callable=AsyncMock) as mock_service:
        response = await async_client.post("/api/v1/auth/request-otp", json={"phone_number": "+221770000000"})
        assert response.status_code == 200
        assert response.json() == {"message": "OTP sent successfully"}
        mock_service.assert_awaited_once()

@pytest.mark.asyncio
async def test_verify_otp_success(async_client):
    with patch("app.modules.auth.router.service.verify_otp_and_login", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = {"access_token": "fake_token", "refresh_token": "fake_refresh", "token_type": "bearer", "user_id": 99}
        
        response = await async_client.post("/api/v1/auth/verify", json={"phone_number": "+221770000000", "code": "1234"})
        
        assert response.status_code == 200
        assert response.json() == {"access_token": "fake_token", "refresh_token": "fake_refresh", "token_type": "bearer"}
        mock_verify.assert_awaited_once()

@pytest.mark.asyncio
async def test_verify_otp_with_session(async_client):
    with patch("app.modules.auth.router.service.verify_otp_and_login", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = {"access_token": "fake_token", "refresh_token": "fake_refresh", "token_type": "bearer", "user_id": 99}
        
        with patch("app.modules.athletes.services.merge_guest_orders", new_callable=AsyncMock) as mock_merge:
            response = await async_client.post("/api/v1/auth/verify", json={"phone_number": "+221770000000", "code": "1234"}, headers={"X-Session-ID": "guest123"})
            
            assert response.status_code == 200
            mock_verify.assert_awaited_once()
            mock_merge.assert_awaited_once_with(unittest.mock.ANY, 99, "guest123")

@pytest.mark.asyncio
async def test_verify_otp_failure(async_client):
    with patch("app.modules.auth.service.verify_otp_and_login", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = None
        
        response = await async_client.post("/api/v1/auth/verify", json={"phone_number": "+221770000000", "code": "0000"})
        
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_otp_lockout_integration(async_client, db_session):
    from app.modules.auth.models import OTPCode
    from datetime import datetime, timezone, timedelta
    
    phone = "+221779998888"
    # Create OTP directly in DB
    otp_code = OTPCode(
        phone_number=phone, 
        code="123456", 
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db_session.add(otp_code)
    await db_session.commit()
    
    from app.core.limiter import limiter
    limiter.reset()

    # Send 4 bad codes -> 401
    for _ in range(4):
        response = await async_client.post("/api/v1/auth/verify", json={"phone_number": phone, "code": "000000"})
        assert response.status_code == 401
        
    # Send 5th bad code -> 400 Lockout
    response = await async_client.post("/api/v1/auth/verify", json={"phone_number": phone, "code": "000000"})
    assert response.status_code == 400
    assert "Trop de tentatives" in response.json()["detail"]
    
    limiter.reset()
    
    # Send correct code after lockout -> 400 Lockout
    response = await async_client.post("/api/v1/auth/verify", json={"phone_number": phone, "code": "123456"})
    assert response.status_code == 400
    assert "Trop de tentatives" in response.json()["detail"]
    
    # Request a new OTP -> success (resetting state implicitly as a new OTP is created)
    with patch("app.infrastructure.sms_client.sms_client.send_otp", new_callable=AsyncMock) as mock_send:
        response = await async_client.post("/api/v1/auth/request-otp", json={"phone_number": phone})
        assert response.status_code == 200
        
    # Test < 5 attempts then correct code
    phone2 = "+221778887777"
    otp2 = OTPCode(
        phone_number=phone2, 
        code="654321", 
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db_session.add(otp2)
    await db_session.commit()
    
    limiter.reset()
    for _ in range(3):
        res = await async_client.post("/api/v1/auth/verify", json={"phone_number": phone2, "code": "000000"})
        assert res.status_code == 401
        
    res_success = await async_client.post("/api/v1/auth/verify", json={"phone_number": phone2, "code": "654321"})
    assert res_success.status_code == 200

    # Test expired OTP
    phone3 = "+221776665555"
    otp3 = OTPCode(
        phone_number=phone3, 
        code="999999", 
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1) # Expired
    )
    db_session.add(otp3)
    await db_session.commit()
    
    limiter.reset()
    res_expired = await async_client.post("/api/v1/auth/verify", json={"phone_number": phone3, "code": "999999"})
    assert res_expired.status_code == 401

@pytest.mark.asyncio
async def test_otp_rate_limit(async_client):
    phone = "+221775554444"
    from app.core.limiter import limiter
    limiter.reset()
    
    # request-otp has limit 3/minute
    with patch("app.modules.auth.service.generate_and_send_otp", new_callable=AsyncMock):
        for _ in range(3):
            response = await async_client.post("/api/v1/auth/request-otp", json={"phone_number": phone})
            assert response.status_code == 200
            
        # 4th request should fail with 429
        response = await async_client.post("/api/v1/auth/request-otp", json={"phone_number": phone})
        assert response.status_code == 429

@pytest.mark.asyncio
async def test_get_me(async_client, db_session):
    # Prepare User
    user = User(phone_number="+221771112233")
    db_session.add(user)
    await db_session.commit()
    
    from app.main import app
    from app.modules.auth.service import get_current_user
    
    app.dependency_overrides[get_current_user] = lambda: user
    
    response = await async_client.get("/api/v1/auth/me")
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
    
    response = await async_client.put("/api/v1/auth/me/profile", json=payload)
    
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
    
    response = await async_client.put("/api/v1/auth/me/profile", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "New Name"
    assert data["bio"] == "New Bio"
    
    await db_session.refresh(profile)
    
    app.dependency_overrides.clear()
