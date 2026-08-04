from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.core.database import get_db
from app.modules.auth.service import get_current_user_optional, get_current_user
from app.modules.auth.models import User
from app.modules.athletes.schemas import (
    TimelineResponse, 
    SlugSuggestionsResponse,
    AthleteProfileCreate,
    AthleteProfileUpdate,
    PublicAthleteProfileResponse
)
from app.modules.athletes.services import (
    get_athlete_timeline,
    get_slug_suggestions,
    create_athlete_profile,
    update_athlete_profile
)
from app.modules.athletes.models import AthleteProfile, AthleteStatistics

router = APIRouter(tags=["Athletes"])

@router.get("/slug-suggestions", response_model=SlugSuggestionsResponse)
async def suggest_slug(
    base_slug: str,
    db: AsyncSession = Depends(get_db)
):
    return await get_slug_suggestions(db, base_slug)

@router.post("/me/profile", response_model=PublicAthleteProfileResponse)
async def create_profile(
    profile_in: AthleteProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        profile = await create_athlete_profile(db, current_user.id, profile_in)
        # Initialize stats for new profile
        stats = AthleteStatistics(
            user_id=current_user.id,
            competitions=0,
            photos=0,
            disciplines=0,
            albums=0,
            photographers=0,
            active_since_year=None
        )
        db.add(stats)
        await db.commit()
        await db.refresh(stats)
        profile.statistics = stats
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/profile", response_model=PublicAthleteProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AthleteProfile).filter(AthleteProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profil non trouvé")
        
    stats_result = await db.execute(select(AthleteStatistics).filter(AthleteStatistics.user_id == current_user.id))
    stats = stats_result.scalar_one_or_none()
    if not stats:
        stats = AthleteStatistics(user_id=current_user.id)
    profile.statistics = stats
    
    return profile

@router.put("/me/profile", response_model=PublicAthleteProfileResponse)
async def update_profile(
    profile_in: AthleteProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        profile = await update_athlete_profile(db, current_user.id, profile_in)
        
        stats_result = await db.execute(select(AthleteStatistics).filter(AthleteStatistics.user_id == current_user.id))
        stats = stats_result.scalar_one_or_none()
        if not stats:
            stats = AthleteStatistics(user_id=current_user.id)
        profile.statistics = stats
        
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/timeline", response_model=TimelineResponse)
async def get_timeline(
    x_session_id: Optional[str] = Header(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    if not current_user and not x_session_id:
        raise HTTPException(status_code=401, detail="Authentication or X-Session-ID required")
        
    user_id = current_user.id if current_user else None
    
    return await get_athlete_timeline(
        db=db,
        user_id=user_id,
        session_id=x_session_id if not user_id else None
    )
