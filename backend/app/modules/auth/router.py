from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.core.database import get_db
from app.modules.auth.schemas import OTPRequest, OTPVerify, Token, UserResponse, PhotographerProfileUpdate, PhotographerProfileResponse
from app.modules.auth import service
from app.modules.auth.models import User, PhotographerProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/request-otp")
async def request_otp(data: OTPRequest, db: AsyncSession = Depends(get_db)):
    await service.generate_and_send_otp(db, data.phone_number)
    return {"message": "OTP sent successfully"}

from fastapi import Header

@router.post("/verify")
async def verify_otp(
    data: OTPVerify, 
    x_session_id: str | None = Header(None),
    db: AsyncSession = Depends(get_db)
) -> Token:
    result = await service.verify_otp_and_login(db, data.phone_number, data.code)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP code",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Trigger guest merging if session_id is present
    if x_session_id:
        from app.modules.athletes.services import merge_guest_orders
        await merge_guest_orders(db, result["user_id"], x_session_id)
        
    return Token(**result)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(service.get_current_user), db: AsyncSession = Depends(get_db)):
    # Load profile
    result = await db.execute(
        select(User).options(selectinload(User.photographer_profile)).where(User.id == current_user.id)
    )
    return result.scalars().first()

@router.put("/me/profile", response_model=PhotographerProfileResponse)
async def update_profile(profile_data: PhotographerProfileUpdate, current_user: User = Depends(service.get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PhotographerProfile).where(PhotographerProfile.user_id == current_user.id))
    profile = result.scalars().first()
    
    if not profile:
        profile = PhotographerProfile(user_id=current_user.id, **profile_data.model_dump(exclude_unset=True))
        db.add(profile)
        # Activer le statut photographe
        current_user.is_photographer = True
    else:
        for key, value in profile_data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
            
    await db.commit()
    await db.refresh(profile)
    return profile
