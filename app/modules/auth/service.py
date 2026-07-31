import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.auth.models import User, OTPCode
from app.infrastructure.email_client import email_client
from app.core.security import create_access_token

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, email: str) -> User:
    db_user = User(email=email)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def generate_and_send_otp(db: AsyncSession, email: str):
    code = str(random.randint(100000, 999999))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    otp = OTPCode(email=email, code=code, expires_at=expires_at)
    db.add(otp)
    await db.commit()
    
    # Envoi simulé via client
    await email_client.send_otp(email, code)
    return True

async def verify_otp_and_login(db: AsyncSession, email: str, code: str):
    # Trouver le code actif
    stmt = select(OTPCode).where(
        OTPCode.email == email,
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
    
    # Utilisateur
    user = await get_user_by_email(db, email)
    if not user:
        user = await create_user(db, email)
        
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
