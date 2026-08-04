from sqlalchemy import JSON
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.core.database import Base
from app.modules.auth.models import User # Ensure User is in registry

class PhotoStatus(str, enum.Enum):
    PENDING = "PENDING"
    UPLOADED = "UPLOADED"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

class Competition(Base):
    __tablename__ = "competitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    photographer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    is_public = Column(Boolean, default=True)
    access_code = Column(String, nullable=True)
    
    # Flexible settings (JSON) to store location, sport, categories, price, etc.
    settings = Column(JSON, nullable=True, default={})
    
    # Packs configuration
    packs_enabled = Column(Boolean, default=False)
    packs = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    photographer = relationship("User", backref="competitions")
    epreuves = relationship("Epreuve", back_populates="competition", cascade="all, delete-orphan")

class Epreuve(Base):
    __tablename__ = "epreuves"

    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    name = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    competition = relationship("Competition", back_populates="epreuves")
    photos = relationship("Photo", back_populates="epreuve", cascade="all, delete-orphan")

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    epreuve_id = Column(Integer, ForeignKey("epreuves.id"), nullable=False)
    
    # Original high-res image key in MinIO
    s3_object_key = Column(String, nullable=False, unique=True)
    # Low-res watermarked image key in MinIO
    watermark_s3_key = Column(String, nullable=True)
    
    status = Column(SQLEnum(PhotoStatus), default=PhotoStatus.PENDING, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    epreuve = relationship("Epreuve", back_populates="photos")
    favorites = relationship("Favorite", back_populates="photo", cascade="all, delete-orphan")

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=True) # For guest users (UUID)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # For authenticated athletes
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    photo = relationship("Photo", back_populates="favorites")
    user = relationship("User", backref="favorites")
