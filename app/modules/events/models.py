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

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    date = Column(DateTime, nullable=False)
    photographer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    is_public = Column(Boolean, default=True)
    access_code = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    photographer = relationship("User", backref="events")
    albums = relationship("Album", back_populates="event", cascade="all, delete-orphan")

class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    name = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    event = relationship("Event", back_populates="albums")
    photos = relationship("Photo", back_populates="album", cascade="all, delete-orphan")

class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=False)
    
    # Original high-res image key in MinIO
    s3_object_key = Column(String, nullable=False, unique=True)
    # Low-res watermarked image key in MinIO
    watermark_s3_key = Column(String, nullable=True)
    
    status = Column(SQLEnum(PhotoStatus), default=PhotoStatus.PENDING, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    album = relationship("Album", back_populates="photos")
