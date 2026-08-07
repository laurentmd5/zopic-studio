from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import date

# Base Models
class AthleteSportAttributes(BaseModel):
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    weight_kg: Optional[float] = Field(None, ge=30, le=200)
    position: Optional[str] = None
    dominant_side: Optional[str] = None
class CompetitionTimelineItem(BaseModel):
    id: str | int
    name: str
    date: str
    sport: str
    location: str
    photos_count: int
    cover_photo_url: str

class YearGroup(BaseModel):
    year: int
    competitions: List[CompetitionTimelineItem]

class TimelineResponse(BaseModel):
    timeline: List[YearGroup]
    total_competitions: int
    total_photos: int
    message: str

# Gallery Models
class AthleteGalleryCreate(BaseModel):
    photo_id: int
    order: Optional[int] = 0

class AthleteGalleryResponse(BaseModel):
    id: int
    user_id: int
    photo_id: int
    order: int
    
    class Config:
        from_attributes = True

# Share Models
class AthleteShareCreate(BaseModel):
    title: str
    url: str

class AthleteShareResponse(BaseModel):
    id: int
    user_id: int
    title: str
    url: str
    type: str
    
    class Config:
        from_attributes = True

# Profile Models
class AthleteProfileUpdate(BaseModel):
    slug: Optional[str] = Field(None, pattern=r'^[a-z0-9\._-]+$')
    is_public: Optional[str] = None
    bio: Optional[str] = None
    club: Optional[str] = None
    nationality: Optional[str] = None
    birth_date: Optional[date] = None
    sport_attributes: Optional[AthleteSportAttributes] = None
    theme_color: Optional[str] = None
    profile_photo_url: Optional[str] = None
    cover_photo_url: Optional[str] = None
    favorite_photo_id: Optional[int] = None

class AthleteProfileCreate(AthleteProfileUpdate):
    slug: str = Field(pattern=r'^[a-z0-9\._-]+$')

class AthleteStatisticsResponse(BaseModel):
    competitions: int
    photos: int
    disciplines: int
    albums: int
    photographers: int
    active_since_year: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class PublicAthleteProfileResponse(BaseModel):
    id: int
    slug: str
    is_public: str
    bio: Optional[str]
    club: Optional[str]
    nationality: Optional[str]
    birth_date: Optional[date]
    sport_attributes: Optional[AthleteSportAttributes] = None
    theme_color: str
    is_verified: bool
    profile_photo_url: Optional[str]
    cover_photo_url: Optional[str]
    favorite_photo_id: Optional[int]
    
    statistics: Optional[AthleteStatisticsResponse] = None
    
    class Config:
        from_attributes = True

class SlugSuggestionsResponse(BaseModel):
    suggestions: List[str]
