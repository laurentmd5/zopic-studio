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
    PublicAthleteProfileResponse,
    AthleteGalleryResponse,
    AthleteGalleryCreate,
    AthleteShareResponse,
    AthleteShareCreate
)
from app.modules.athletes.services import (
    get_athlete_timeline,
    get_slug_suggestions,
    create_athlete_profile,
    update_athlete_profile,
    get_athlete_gallery,
    add_photo_to_gallery,
    remove_photo_from_gallery,
    get_athlete_shares,
    add_athlete_share,
    remove_athlete_share
)
from app.modules.athletes.models import AthleteProfile, AthleteStatistics
from typing import List

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
            photographers=0
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
        raise HTTPException(status_code=404, detail="Profil non trouvÃ©")
        
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
            stats = AthleteStatistics(
                user_id=current_user.id,
                competitions=0,
                photos=0,
                disciplines=0,
                albums=0,
                photographers=0
            )
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

# Gallery Endpoints
@router.get("/me/gallery", response_model=List[AthleteGalleryResponse])
async def get_gallery(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_athlete_gallery(db, current_user.id)

@router.post("/me/gallery", response_model=AthleteGalleryResponse)
async def add_to_gallery(
    gallery_in: AthleteGalleryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await add_photo_to_gallery(db, current_user.id, gallery_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/me/gallery/{photo_id}")
async def remove_from_gallery(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        await remove_photo_from_gallery(db, current_user.id, photo_id)
        return {"detail": "Photo retirée de la galerie"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Share Endpoints
@router.get("/me/shares", response_model=List[AthleteShareResponse])
async def get_shares(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_athlete_shares(db, current_user.id)

@router.post("/me/shares", response_model=AthleteShareResponse)
async def add_share(
    share_in: AthleteShareCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await add_athlete_share(db, current_user.id, share_in)

@router.delete("/me/shares/{share_id}")
async def remove_share(
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        await remove_athlete_share(db, current_user.id, share_id)
        return {"detail": "Lien supprimé"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
