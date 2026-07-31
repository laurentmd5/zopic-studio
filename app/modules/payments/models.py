import enum
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base
from app.modules.auth.models import User
from app.modules.events.models import Photo

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for guest checkout
    total_amount = Column(Integer, nullable=False) # En FCFA
    status = Column(String, default=OrderStatus.PENDING)
    paydunya_token = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    buyer = relationship("User", backref="orders")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    price = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    photo = relationship("Photo")

class PhotoSale(Base):
    """Ledger table (immuable)"""
    __tablename__ = "photo_sales"

    id = Column(Integer, primary_key=True, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), unique=True, nullable=False)
    photographer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount_total = Column(Integer, nullable=False)
    amount_photographer = Column(Integer, nullable=False) # 75%
    amount_platform = Column(Integer, nullable=False) # 25%
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    order_item = relationship("OrderItem")
    photographer = relationship("User")

class PayoutStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"

class Payout(Base):
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    photographer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default=PayoutStatus.PENDING)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    photographer = relationship("User")
