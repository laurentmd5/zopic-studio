from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import date

# Base Models
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

# Profile Models
class AthleteProfileUpdate(BaseModel):
    slug: Optional[str] = Field(None, pattern=r'^[a-z0-9\._-]+$')
    is_public: Optional[str] = None
    bio: Optional[str] = None
    club: Optional[str] = None
    nationality: Optional[str] = None
    birth_date: Optional[date] = None
    sport_attributes: Optional[Dict[str, Any]] = None
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
    active_since_year: Optional[int]

class PublicAthleteProfileResponse(BaseModel):
    id: int
    slug: str
    is_public: str
    bio: Optional[str]
    club: Optional[str]
    nationality: Optional[str]
    birth_date: Optional[date]
    sport_attributes: Dict[str, Any]
    theme_color: str
    is_verified: bool
    profile_photo_url: Optional[str]
    cover_photo_url: Optional[str]
    favorite_photo_id: Optional[int]
    
    statistics: AthleteStatisticsResponse
    
    class Config:
        from_attributes = True

class SlugSuggestionsResponse(BaseModel):
    suggestions: List[str]
