from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.schemas import OTPRequest, OTPVerify, Token
from app.modules.auth import service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/request-otp")
async def request_otp(data: OTPRequest, db: AsyncSession = Depends(get_db)):
    await service.generate_and_send_otp(db, data.email)
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp", response_model=Token)
async def verify_otp(data: OTPVerify, db: AsyncSession = Depends(get_db)):
    result = await service.verify_otp_and_login(db, data.email, data.code)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP code",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result
