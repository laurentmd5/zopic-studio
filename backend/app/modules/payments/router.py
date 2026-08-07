from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
from typing import Dict, Any

from app.core.database import get_db
from app.modules.auth.models import User
from app.modules.payments.schemas import OrderCreate, OrderResponse, PaydunyaWebhook
from app.modules.payments import service

router = APIRouter(prefix="/payments", tags=["Payments"])

from app.core.config import settings

from app.modules.auth.service import get_current_user_optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, Header

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    x_session_id: str | None = Header(None),
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """Créer une commande et obtenir le lien de paiement PayDunya"""
    user_id = current_user.id if current_user else None
    return await service.create_order(db, order_data, user_id, x_session_id)

@router.post("/paydunya-webhook")
async def paydunya_webhook(
    request: Request,
    payload: PaydunyaWebhook,
    paydunya_signature: str | None = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook officiel PayDunya (IPN).
    Vérifie la signature HMAC avant de traiter le paiement.
    """
    if not paydunya_signature:
        raise HTTPException(status_code=403, detail="Signature manquante")
        
    # Validation HMAC SHA256
    body = await request.body()
    secret_bytes = settings.PAYMENT_WEBHOOK_SECRET.encode('utf-8')
    computed_hmac = hmac.new(secret_bytes, body, hashlib.sha256).hexdigest()
    
    if not hmac.compare_digest(computed_hmac, paydunya_signature):
        raise HTTPException(status_code=403, detail="Signature invalide")
        
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
    if not getattr(settings, "PAYMENT_SIMULATION_MODE", False):
        raise HTTPException(status_code=403, detail="Simulation non autorisée en production")
        
    is_success = (status == "completed")
    return await service.process_webhook(db, token, is_success)

from app.modules.payments.models import Order, OrderStatus

@router.get("/purchases")
async def get_purchases(
    x_session_id: str | None = Header(None),
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère l'historique des achats pour l'utilisateur connecté ou l'invité.
    """
    user_id = current_user.id if current_user else None
    
    if not user_id and not x_session_id:
        return []
        
    from sqlalchemy.future import select
    query = select(Order).where(Order.status == OrderStatus.PAID)
    
    if user_id:
        query = query.where(Order.user_id == user_id)
    else:
        query = query.where(Order.session_id == x_session_id)
        
    query = query.order_by(Order.created_at.desc())
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    response = []
    from app.modules.payments.models import OrderItem
    from app.modules.downloads.models import DownloadPermission
    from app.modules.archives.models import Archive
    
    for order in orders:
        # Load items
        items_res = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
        items = items_res.scalars().all()
        
        # Load permissions
        perm_res = await db.execute(select(DownloadPermission).where(DownloadPermission.order_id == order.id))
        permission = perm_res.scalars().first()
        
        # Load archive status
        archive_res = await db.execute(select(Archive).where(Archive.order_id == order.id))
        archive = archive_res.scalars().first()
        
        response.append({
            "id": order.id,
            "total_amount": order.total_amount,
            "created_at": order.created_at,
            "items_count": len(items),
            "permission_expires_at": permission.expires_at if permission else None,
            "archive_status": archive.status if archive else None,
            "archive_id": archive.id if archive else None,
            "items": [{"photo_id": item.photo_id} for item in items]
        })
        
    return response
