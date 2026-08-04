import asyncio
import os
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
import logging

from app.core.database import get_db
from app.modules.payments.models import OrderItem, Order
from app.modules.competitions.models import Photo
from app.modules.downloads.models import DownloadPermission
from app.modules.archives.models import Archive, ArchiveStatus, ArchiveType

from arq import create_pool
from arq.connections import RedisSettings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["Archives"])

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

async def get_redis_pool():
    return await create_pool(RedisSettings.from_dsn(REDIS_URL))

@router.post("/{order_id}/archives")
async def create_archive(
    order_id: int,
    request: Request,
    x_session_id: str | None = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Déclenche la création asynchrone d'une archive ZIP pour la commande.
    """
    # 1. Vérifier la commande et la permission
    order_res = await db.execute(select(Order).where(Order.id == order_id))
    order = order_res.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable.")
        
    perm_res = await db.execute(select(DownloadPermission).where(DownloadPermission.order_id == order_id))
    permission = perm_res.scalars().first()
    if not permission or permission.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="Droit de téléchargement invalide ou expiré.")

    # 2. Vérifier si une archive est déjà en cours ou terminée
    archive_res = await db.execute(select(Archive).where(
        Archive.order_id == order_id,
        Archive.archive_type == ArchiveType.ZIP
    ))
    archive = archive_res.scalars().first()
    
    if archive and archive.status in [ArchiveStatus.PROCESSING, ArchiveStatus.COMPLETED]:
        return {"archive_id": archive.id, "status": archive.status}
        
    if not archive:
        archive = Archive(
            order_id=order_id,
            archive_type=ArchiveType.ZIP,
            status=ArchiveStatus.PENDING
        )
        db.add(archive)
        await db.commit()
        await db.refresh(archive)
    else:
        archive.status = ArchiveStatus.PENDING
        await db.commit()

    # 3. Récupérer les clés S3 des photos de la commande
    items_res = await db.execute(select(OrderItem).where(OrderItem.order_id == order_id))
    items = items_res.scalars().all()
    photo_ids = [item.photo_id for item in items]
    
    photos_res = await db.execute(select(Photo).where(Photo.id.in_(photo_ids)))
    photos = photos_res.scalars().all()
    
    s3_keys = [f"originals/{p.s3_object_key.split('/')[-1]}" for p in photos]

    # 4. Enqueue la tâche sur Redis
    # Note: On utilise aiohttp post callback pour le worker_ai pour qu'il notifie le webhook
    # L'API backend est par ex: http://backend:8000/api/v1/orders/{order_id}/archives/{archive.id}/callback
    backend_url = os.getenv("BACKEND_URL", "http://backend:8000")
    callback_url = f"{backend_url}/api/v1/orders/{order_id}/archives/{archive.id}/callback"
    
    redis = await get_redis_pool()
    await redis.enqueue_job("generate_zip", archive.id, s3_keys, callback_url, _queue_name='arq:ai_queue')
    
    archive.status = ArchiveStatus.PROCESSING
    await db.commit()
    
    return {"archive_id": archive.id, "status": archive.status}

from pydantic import BaseModel
class ArchiveCallback(BaseModel):
    status: str
    s3_object_key: str | None = None
    size: int | None = None

@router.post("/{order_id}/archives/{archive_id}/callback")
async def archive_callback(
    order_id: int,
    archive_id: int,
    payload: ArchiveCallback,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook interne appelé par le Worker quand le ZIP est prêt.
    """
    archive_res = await db.execute(select(Archive).where(Archive.id == archive_id))
    archive = archive_res.scalars().first()
    if not archive:
        raise HTTPException(status_code=404)
        
    archive.status = payload.status
    if payload.s3_object_key:
        archive.s3_object_key = payload.s3_object_key
    if payload.size:
        archive.size = payload.size
        
    await db.commit()
    # Le SSE stream lira ce changement dans la base
    return {"status": "ok"}

@router.get("/{order_id}/archives/{archive_id}/stream")
async def archive_sse_stream(
    order_id: int,
    archive_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Stream (Server-Sent Events) pour avertir le client quand l'archive est COMPLETED.
    """
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
                
            archive_res = await db.execute(select(Archive).where(Archive.id == archive_id))
            archive = archive_res.scalars().first()
            
            if not archive:
                yield {"data": "error: not_found"}
                break
                
            if archive.status == ArchiveStatus.COMPLETED:
                from app.modules.storage.service import generate_download_url
                url = await generate_download_url(archive.s3_object_key, expiration=900)
                yield {"event": "completed", "data": f'{{"url": "{url}"}}'}
                break
            elif archive.status == ArchiveStatus.FAILED:
                yield {"event": "failed", "data": "error"}
                break
                
            yield {"event": "processing", "data": "waiting"}
            await asyncio.sleep(2) # Polling DB toutes les 2s pour le SSE (Simple MVP)
            
    return EventSourceResponse(event_generator())
