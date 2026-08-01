from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.payments.schemas import OrderCreate, OrderResponse, PaydunyaWebhook
from app.modules.payments import service

router = APIRouter(prefix="/payments", tags=["Payments"])

async def get_current_user_optional() -> User | None:
    # Mock user for MVP, can return None for guest checkout
    return None

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """CrÃ©er une commande et obtenir le lien de paiement PayDunya"""
    user_id = current_user.id if current_user else None
    return await service.create_order(db, order_data, user_id)

@router.post("/webhook/paydunya")
async def paydunya_webhook(
    request: Request,
    payload: PaydunyaWebhook,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook officiel PayDunya (IPN).
    En production, on vÃ©rifierait le master_key et le hash ici.
    Pour l'instant, on lit juste le token et le statut de la requÃªte form-data ou JSON.
    """
    # Ex: on suppose que PayDunya envoie le token dans data.token et le statut dans data.status
    data = payload.data
    token = data.get("token")
    status_str = data.get("status")
    
    if not token:
        raise HTTPException(status_code=400, detail="Token manquant")
        
    is_success = (status_str == "completed")
    return await service.process_webhook(db, token, is_success)

@router.post("/simulate-webhook")
async def simulate_webhook(
    token: str,
    status: str = "completed",
    db: AsyncSession = Depends(get_db)
):
    """
    Route utilitaire (dev) pour simuler un webhook PayDunya.
    """
    is_success = (status == "completed")
    return await service.process_webhook(db, token, is_success)
