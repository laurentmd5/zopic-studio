from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class PlanBase(BaseModel):
    name: str
    storage_limit_gb: int
    price_monthly: int
    is_active: bool

class PlanResponse(PlanBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class SubscriptionBase(BaseModel):
    plan_id: int

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class StorageUsageResponse(BaseModel):
    id: int
    user_id: int
    used_bytes: float
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
