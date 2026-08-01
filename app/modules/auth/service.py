import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError

from app.modules.auth.models import User, OTPCode, PhotographerProfile
from app.infrastructure.sms_client import sms_client
from app.core.security import create_access_token, ALGORITHM
from app.core.config import settings
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/verify")

async def get_user_by_phone(db: AsyncSession, phone_number: str) -> User | None:
    result = await db.execute(select(User).where(User.phone_number == phone_number))
    return result.scalars().first()

async def create_user(db: AsyncSession, phone_number: str) -> User:
    db_user = User(phone_number=phone_number)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def generate_and_send_otp(db: AsyncSession, phone_number: str):
    code = str(random.randint(100000, 999999))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    otp = OTPCode(phone_number=phone_number, code=code, expires_at=expires_at)
    db.add(otp)
    await db.commit()
    
    await sms_client.send_otp(phone_number, code)
    return True

async def verify_otp_and_login(db: AsyncSession, phone_number: str, code: str):
    stmt = select(OTPCode).where(
        OTPCode.phone_number == phone_number,
        OTPCode.code == code,
        OTPCode.is_used == False,
        OTPCode.expires_at > datetime.now(timezone.utc)
    ).order_by(OTPCode.id.desc())
    
    result = await db.execute(stmt)
    otp = result.scalars().first()
    
    if not otp:
        return None
        
    otp.is_used = True
    await db.commit()
    
    user = await get_user_by_phone(db, phone_number)
    if not user:
        user = await create_user(db, phone_number)
        
    access_token = create_access_token(data={"sub": user.phone_number})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
    except (jwt.PyJWTError, ValidationError):
        raise credentials_exception
        
    user = await get_user_by_phone(db, phone_number)
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_optional(token: str = Depends(OAuth2PasswordBearer(tokenUrl="api/v1/auth/verify", auto_error=False)), db: AsyncSession = Depends(get_db)) -> User | None:
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
