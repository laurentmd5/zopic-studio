from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
import uuid
import logging

from app.core.database import get_db
from app.modules.payments.models import OrderItem, Order
from app.modules.competitions.models import Photo
from app.modules.downloads.models import DownloadPermission, DownloadToken, DownloadLog, DownloadSource, DownloadType
from app.modules.storage.service import generate_download_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Downloads"])

@router.get("/{order_id}/photos/{photo_id}/download")
async def download_photo(
    order_id: int,
    photo_id: int,
    request: Request,
    x_session_id: str | None = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Génère une Presigned URL courte durée pour télécharger une photo individuelle.
    """
    print(f"DEBUG: Executing download_photo for order_id={order_id}, photo_id={photo_id}")
    # 1. Vérifier la commande (et l'identité si session_id/user_id)
    order_res = await db.execute(select(Order).where(Order.id == order_id))
    order = order_res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable.")
    
    # Simple vérification (en prod, vérifier current_user ou session_id)
    if order.session_id and x_session_id and order.session_id != x_session_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé.")

    # 2. Vérifier que la photo fait partie de la commande
    item_res = await db.execute(select(OrderItem).where(
        OrderItem.order_id == order_id,
        OrderItem.photo_id == photo_id
    ))
    if not item_res.scalars().first():
        raise HTTPException(status_code=403, detail="Cette photo n'appartient pas à cette commande.")

    # 3. Vérifier la Permission
    perm_res = await db.execute(select(DownloadPermission).where(DownloadPermission.order_id == order_id))
    permission = perm_res.scalars().first()
    if not permission:
        raise HTTPException(status_code=403, detail="Aucun droit de téléchargement pour cette commande.")
    
    if permission.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Le droit de téléchargement a expiré.")

    # 4. Créer un Token éphémère (traçabilité)
    token = str(uuid.uuid4())
    download_token = DownloadToken(
        permission_id=permission.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    db.add(download_token)

    # 5. Log de l'action
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    log = DownloadLog(
        order_id=order_id,
        photo_id=photo_id,
        ip_address=client_ip,
        user_agent=user_agent,
        download_source=DownloadSource.WEB,
        download_type=DownloadType.SINGLE
    )
    db.add(log)
    
    # 6. Récupérer la photo et l'URL S3
    photo_res = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = photo_res.scalars().first()
    
    object_key = photo.s3_object_key

    # Générer la Presigned URL (valide 15 minutes)
    presigned_url = await generate_download_url(object_key, expiration=900)
    
    await db.commit()
    
    return {"download_url": presigned_url}
