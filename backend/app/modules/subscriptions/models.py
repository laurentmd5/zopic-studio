from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.core.database import Base

class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    storage_limit_gb = Column(Integer, nullable=False)
    price_monthly = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    EXPIRED = "EXPIRED"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    
    start_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    provider = Column(String, nullable=True)
    payment_reference = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", backref="subscriptions")
    plan = relationship("Plan")

class StorageUsage(Base):
    __tablename__ = "storage_usages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    used_bytes = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", backref="storage_usage")
