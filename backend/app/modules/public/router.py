from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.modules.athletes.models import AthleteProfile, AthleteStatistics, PrivacyLevel
from app.modules.athletes.schemas import PublicAthleteProfileResponse
from app.modules.athletes.services import get_athlete_timeline

router = APIRouter(tags=["Public"])

@router.get("/athletes/{slug}", response_model=PublicAthleteProfileResponse)
async def get_public_athlete_profile(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    # Retrieve profile
    result = await db.execute(
        select(AthleteProfile).filter(AthleteProfile.slug == slug)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
        
    if not profile.is_activated:
        raise HTTPException(status_code=404, detail="Profile not activated")
        
    if profile.is_public == PrivacyLevel.PRIVATE:
        raise HTTPException(status_code=404, detail="Profile is private")
        
    # Retrieve statistics
    stats_result = await db.execute(
        select(AthleteStatistics).filter(AthleteStatistics.user_id == profile.user_id)
    )
    stats = stats_result.scalar_one_or_none()
    
    # Fallback to zero stats if not initialized
    if not stats:
        stats = AthleteStatistics(
            user_id=profile.user_id,
            competitions=0,
            photos=0,
            disciplines=0,
            albums=0,
            photographers=0
        )
        
    # Set the statistics on the profile object (Pydantic will pick it up via from_attributes)
    profile.statistics = stats
    
    return profile
