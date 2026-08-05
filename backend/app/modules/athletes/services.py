from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from app.modules.payments.models import Order, OrderItem, OrderStatus
from app.modules.competitions.models import Photo, Epreuve, Competition
from app.modules.athletes.schemas import TimelineResponse, YearGroup, CompetitionTimelineItem, AthleteGalleryCreate, AthleteShareCreate
from app.modules.storage.service import generate_download_url
from collections import defaultdict
from typing import Optional

async def get_athlete_timeline(db: AsyncSession, user_id: Optional[int], session_id: Optional[str]) -> TimelineResponse:
    if not user_id and not session_id:
        return TimelineResponse(timeline=[], total_competitions=0, total_photos=0, message="Veuillez vous connecter")

    order_filter = []
    if user_id:
        order_filter.append(Order.user_id == user_id)
    if session_id:
        order_filter.append(Order.session_id == session_id)
    
    query = (
        select(
            Epreuve,
            Competition,
            func.count(OrderItem.id).label("photos_count"),
            func.min(Photo.s3_object_key).label("cover_key")
        )
        .join(Competition, Competition.id == Epreuve.competition_id)
        .join(Photo, Photo.epreuve_id == Epreuve.id)
        .join(OrderItem, OrderItem.photo_id == Photo.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status == OrderStatus.PAID)
        .filter(or_(*order_filter))
        .group_by(Epreuve.id, Competition.id)
        .order_by(Competition.date.desc())
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    total_competitions = len(rows) # Actually total albums now
    total_photos = sum(r.photos_count for r in rows)
    
    years_dict = defaultdict(list)
    for epreuve, comp, photos_count, cover_key in rows:
        year = comp.date.year
        settings = comp.settings or {}
        sport = settings.get("sport", "Autres")
        location = settings.get("location", "Non spécifié")
        
        cover_url = await generate_download_url(cover_key) if cover_key else ""
        
        item = CompetitionTimelineItem(
            id=epreuve.id,
            name=f"{comp.name} - {epreuve.name}",
            date=comp.date.isoformat(),
            sport=sport,
            location=location,
            photos_count=photos_count,
            cover_photo_url=cover_url
        )
        years_dict[year].append(item)
        
    timeline = []
    for year in sorted(years_dict.keys(), reverse=True):
        timeline.append(YearGroup(year=year, competitions=years_dict[year]))
        
    if total_competitions == 0:
        message = "Aucune compétition pour le moment"
    elif total_competitions == 1:
        message = "Le début d'une grande aventure 🚀"
    elif total_competitions > 10:
        message = "Une carrière bien remplie 💪"
    else:
        message = "Votre carrière sportive en images 🏆"
        
    return TimelineResponse(
        timeline=timeline,
        total_competitions=total_competitions,
        total_photos=total_photos,
        message=message
    )

from app.modules.athletes.models import AthleteProfile
from app.modules.athletes.schemas import SlugSuggestionsResponse
import random

async def get_slug_suggestions(db: AsyncSession, base_slug: str) -> SlugSuggestionsResponse:
    # Check if base is taken
    result = await db.execute(select(AthleteProfile).filter(AthleteProfile.slug == base_slug))
    if not result.scalar_one_or_none():
        return SlugSuggestionsResponse(suggestions=[base_slug])
        
    suggestions = []
    suffixes = ["2", "_sport", ".dkr", ".officiel", f"{random.randint(10, 99)}"]
    
    for suffix in suffixes:
        test_slug = f"{base_slug}{suffix}"
        result = await db.execute(select(AthleteProfile).filter(AthleteProfile.slug == test_slug))
        if not result.scalar_one_or_none():
            suggestions.append(test_slug)
            
    return SlugSuggestionsResponse(suggestions=suggestions)

from app.modules.athletes.schemas import AthleteProfileCreate, AthleteProfileUpdate

async def create_athlete_profile(db: AsyncSession, user_id: int, profile_in: AthleteProfileCreate):
    # Check if user already has a profile
    result = await db.execute(select(AthleteProfile).filter(AthleteProfile.user_id == user_id))
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("L'athlète a déjà un profil.")
        
    # Check if slug is taken
    result_slug = await db.execute(select(AthleteProfile).filter(AthleteProfile.slug == profile_in.slug))
    if result_slug.scalar_one_or_none():
        raise ValueError("Ce nom d'utilisateur est déjà pris.")
        
    new_profile = AthleteProfile(
        user_id=user_id,
        slug=profile_in.slug,
        is_activated=True,
        **profile_in.model_dump(exclude_unset=True, exclude={'slug'})
    )
    
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)
    
    return new_profile

async def update_athlete_profile(db: AsyncSession, user_id: int, profile_in: AthleteProfileUpdate):
    result = await db.execute(select(AthleteProfile).filter(AthleteProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise ValueError("Profil introuvable.")
        
    if profile_in.slug and profile_in.slug != profile.slug:
        result_slug = await db.execute(select(AthleteProfile).filter(AthleteProfile.slug == profile_in.slug))
        if result_slug.scalar_one_or_none():
            raise ValueError("Ce nom d'utilisateur est déjà pris.")
            
    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
        
    await db.commit()
    await db.refresh(profile)
    return profile

async def merge_guest_orders(db: AsyncSession, user_id: int, session_id: str):
    # Update orders to link to user_id where session_id matches
    from sqlalchemy import update
    
    await db.execute(
        update(Order)
        .where(Order.session_id == session_id)
        .values(user_id=user_id, session_id=None)
    )
    await db.commit()

# Gallery Services
async def get_athlete_gallery(db: AsyncSession, user_id: int):
    from app.modules.athletes.models import AthleteGallery
    result = await db.execute(
        select(AthleteGallery)
        .filter(AthleteGallery.user_id == user_id)
        .order_by(AthleteGallery.order.asc())
    )
    return result.scalars().all()

async def add_photo_to_gallery(db: AsyncSession, user_id: int, gallery_in: AthleteGalleryCreate):
    from app.modules.athletes.models import AthleteGallery
    
    # Check if already in gallery
    existing = await db.execute(
        select(AthleteGallery)
        .filter(AthleteGallery.user_id == user_id, AthleteGallery.photo_id == gallery_in.photo_id)
    )
    if existing.scalar_one_or_none():
        raise ValueError("Photo already in gallery")
        
    gallery_item = AthleteGallery(
        user_id=user_id,
        photo_id=gallery_in.photo_id,
        order=gallery_in.order
    )
    db.add(gallery_item)
    await db.commit()
    await db.refresh(gallery_item)
    return gallery_item

async def remove_photo_from_gallery(db: AsyncSession, user_id: int, photo_id: int):
    from app.modules.athletes.models import AthleteGallery
    result = await db.execute(
        select(AthleteGallery)
        .filter(AthleteGallery.user_id == user_id, AthleteGallery.photo_id == photo_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise ValueError("Photo not found in gallery")
        
    await db.delete(item)
    await db.commit()
    return True

# Share Services
async def get_athlete_shares(db: AsyncSession, user_id: int):
    from app.modules.athletes.models import AthleteShare
    result = await db.execute(
        select(AthleteShare)
        .filter(AthleteShare.user_id == user_id)
        .order_by(AthleteShare.created_at.desc())
    )
    return result.scalars().all()

async def add_athlete_share(db: AsyncSession, user_id: int, share_in: AthleteShareCreate):
    from app.modules.athletes.models import AthleteShare, ShareType
    
    # Simple logic to determine type
    share_type = ShareType.LINK
    if "youtube.com" in share_in.url or "youtu.be" in share_in.url:
        share_type = ShareType.YOUTUBE
    elif "article" in share_in.url or "news" in share_in.url:
        share_type = ShareType.ARTICLE
        
    share_item = AthleteShare(
        user_id=user_id,
        title=share_in.title,
        url=share_in.url,
        type=share_type
    )
    db.add(share_item)
    await db.commit()
    await db.refresh(share_item)
    return share_item

async def remove_athlete_share(db: AsyncSession, user_id: int, share_id: int):
    from app.modules.athletes.models import AthleteShare
    result = await db.execute(
        select(AthleteShare)
        .filter(AthleteShare.id == share_id, AthleteShare.user_id == user_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise ValueError("Share not found")
        
    await db.delete(item)
    await db.commit()
    return True

