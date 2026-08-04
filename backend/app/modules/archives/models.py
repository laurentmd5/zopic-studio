from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.core.database import Base
from app.modules.payments.models import Order

class ArchiveType(str, enum.Enum):
    ZIP = "ZIP"
    PDF = "PDF"
    CONTACT_SHEET = "CONTACT_SHEET"

class ArchiveStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Archive(Base):
    __tablename__ = "archives"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    archive_type = Column(SQLEnum(ArchiveType), default=ArchiveType.ZIP, nullable=False)
    status = Column(SQLEnum(ArchiveStatus), default=ArchiveStatus.PENDING, nullable=False)
    
    s3_object_key = Column(String, nullable=True) # Set when COMPLETED
    size = Column(BigInteger, nullable=True) # Bytes
    mime_type = Column(String, nullable=True)
    checksum = Column(String, nullable=True) # SHA256 or MD5 for integrity
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True) # Cloud lifecycle rule target

    order = relationship("Order")
