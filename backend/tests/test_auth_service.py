import pytest
from unittest.mock import patch, AsyncMock
from app.modules.auth.service import (
    create_user, get_user_by_phone, generate_and_send_otp,
    verify_otp_and_login, get_current_user, get_current_user_optional
)
from app.modules.auth.models import User, OTPCode
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from app.core.security import create_access_token
import jwt

@pytest.mark.asyncio
async def test_create_user(db_session):
    user = await create_user(db_session, "+221770000000")
    assert user.phone_number == "+221770000000"

@pytest.mark.asyncio
async def test_get_user_by_phone(db_session):
    await create_user(db_session, "+221770000001")
    user = await get_user_by_phone(db_session, "+221770000001")
    assert user is not None
    assert user.phone_number == "+221770000001"

@pytest.mark.asyncio
async def test_generate_and_send_otp(db_session):
    with patch("app.infrastructure.sms_client.sms_client.send_otp", new_callable=AsyncMock) as mock_send:
        result = await generate_and_send_otp(db_session, "+221770000002")
        assert result is True
        mock_send.assert_called_once()

@pytest.mark.asyncio
async def test_verify_otp_and_login_success(db_session):
    # Setup OTP
    otp_code = OTPCode(
        phone_number="+221770000003", 
        code="123456", 
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
    )
    db_session.add(otp_code)
    await db_session.commit()
    
    # Verify and login
    result = await verify_otp_and_login(db_session, "+221770000003", "123456")
    assert result is not None
    assert "access_token" in result
    
    # User should be created
    user = await get_user_by_phone(db_session, "+221770000003")
    assert user is not None

@pytest.mark.asyncio
async def test_verify_otp_and_login_failure(db_session):
    result = await verify_otp_and_login(db_session, "+221770000004", "000000")
    assert result is None

@pytest.mark.asyncio
async def test_get_current_user_success(db_session):
    await create_user(db_session, "+221770000005")
    token = create_access_token(data={"sub": "+221770000005"})
    
    user = await get_current_user(token, db_session)
    assert user.phone_number == "+221770000005"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session):
    with pytest.raises(HTTPException):
        await get_current_user("invalid.token", db_session)

@pytest.mark.asyncio
async def test_get_current_user_optional(db_session):
    await create_user(db_session, "+221770000006")
    token = create_access_token(data={"sub": "+221770000006"})
    
    user = await get_current_user_optional(token, db_session)
    assert user is not None
    assert user.phone_number == "+221770000006"
    
    user_none = await get_current_user_optional(None, db_session)
    assert user_none is None
