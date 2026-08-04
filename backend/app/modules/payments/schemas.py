from pydantic import BaseModel
from typing import List, Optional
from .models import OrderStatus

class OrderCreate(BaseModel):
    photo_ids: List[int]
    amount_expected: int
    cancel_url: str = "http://localhost:3000/cancel"
    return_url: str = "http://localhost:3000/success"

class OrderResponse(BaseModel):
    order_id: int
    total_amount: int
    paydunya_token: str
    payment_url: str

class PaydunyaWebhook(BaseModel):
    data: dict
    
    # Normally we check the hash to ensure authenticity, 
    # but for simulation we just receive the token and status
    # This schema might be customized based on PayDunya real API
