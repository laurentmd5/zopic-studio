from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.core.database import Base
from app.modules.payments.models import Order
from app.modules.competitions.models import Photo

class DownloadSource(str, enum.Enum):
    WEB = "WEB"
    PWA = "PWA"
    ANDROID = "ANDROID"
    IOS = "IOS"

class DownloadType(str, enum.Enum):
    SINGLE = "SINGLE"
    ZIP = "ZIP"

class DownloadPermission(Base):
    __tablename__ = "download_permissions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    order = relationship("Order")
    tokens = relationship("DownloadToken", back_populates="permission", cascade="all, delete-orphan")

class DownloadToken(Base):
    """Jeton éphémère (ex: 15 min) pour tracer un téléchargement spécifique."""
    __tablename__ = "download_tokens"

    id = Column(Integer, primary_key=True, index=True)
    permission_id = Column(Integer, ForeignKey("download_permissions.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    permission = relationship("DownloadPermission", back_populates="tokens")

class DownloadLog(Base):
    __tablename__ = "download_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=True) # None pour un ZIP
    
    downloaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    country = Column(String, nullable=True)
    device = Column(String, nullable=True)
    
    download_source = Column(SQLEnum(DownloadSource), default=DownloadSource.PWA)
    download_type = Column(SQLEnum(DownloadType), default=DownloadType.SINGLE)
    
    order = relationship("Order")
    photo = relationship("Photo")
