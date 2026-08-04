import enum
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base
from sqlalchemy import JSON

class PrivacyLevel(str, enum.Enum):
    PUBLIC = "PUBLIC"
    LINK_ONLY = "LINK_ONLY"
    PRIVATE = "PRIVATE"

class AthleteProfile(Base):
    __tablename__ = "athlete_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    
    is_activated = Column(Boolean, default=False)
    is_public = Column(String, default=PrivacyLevel.PUBLIC)
    
    bio = Column(String, nullable=True)
    club = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    
    # JSON to store dynamic sport attributes without schema changes
    sport_attributes = Column(JSON, nullable=True, default={})
    
    profile_photo_url = Column(String, nullable=True)
    cover_photo_url = Column(String, nullable=True)
    favorite_photo_id = Column(Integer, ForeignKey("photos.id"), nullable=True)
    
    theme_color = Column(String, default="blue")
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", backref="athlete_profile")
    favorite_photo = relationship("Photo")

class AthleteStatistics(Base):
    __tablename__ = "athlete_statistics"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    
    competitions = Column(Integer, default=0)
    photos = Column(Integer, default=0)
    disciplines = Column(Integer, default=0)
    albums = Column(Integer, default=0)
    photographers = Column(Integer, default=0)
    
    first_event_date = Column(Date, nullable=True)
    
    @property
    def active_since_year(self):
        return self.first_event_date.year if self.first_event_date else None
    
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", backref="statistics")
