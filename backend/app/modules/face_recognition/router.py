import os
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.modules.auth.service import get_current_user
from app.modules.auth.models import User
from app.modules.audit.models import AuditLog
from app.infrastructure.s3_client import s3_client
from datetime import datetime, timezone
from sqlalchemy.future import select
from app.modules.competitions.models import Photo, Epreuve, Competition

router = APIRouter(prefix="/faces", tags=["Face Recognition"])

AI_API_URL = os.getenv("AI_API_URL", "http://localhost:8001")

def get_session_id(request: Request) -> str:
    # Basic session extraction for audit
    return request.headers.get("x-session-id", "guest")

@router.post("/search")
async def search_faces(
    request: Request,
    competition_id: int = Form(...),
    consent: bool = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Proxy pour le worker IA. Envoie le selfie au worker pour extraction
    et recherche dans Qdrant.
    """
    if not consent:
        raise HTTPException(status_code=403, detail="Consent is required for biometric processing")
        
    try:
        if file.size and file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
            
        content = await file.read(10 * 1024 * 1024 + 1)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large (max 10MB)")
            
        # Log the biometric search
        session_id = get_session_id(request)
        audit_log = AuditLog(
            actor_type="user" if session_id != "guest" else "guest",
            actor_id=session_id,
            entity_type="competition",
            entity_id=str(competition_id),
            action="face_search",
            metadata_json={"ip": request.client.host if request.client else "unknown"}
        )
        db.add(audit_log)
        await db.commit()
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_API_URL}/search",
                data={"competition_id": competition_id},
                files={"file": (file.filename, content, file.content_type)},
                timeout=30.0
            )
            
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
            
        # Process response to generate presigned URLs and fetch prices
        data = response.json()
        results = data.get("results", [])
        
        # Get competition to fetch unit_price
        comp_res = await db.execute(select(Competition).where(Competition.id == competition_id))
        competition = comp_res.scalars().first()
        settings = competition.settings if competition and competition.settings else {}
        unit_price = settings.get("price_xof", 1500)
        
        photo_ids = [res.get("photo_id") for res in results if res.get("photo_id")]
        
        if photo_ids:
            photos_res = await db.execute(select(Photo).where(Photo.id.in_(photo_ids)))
            photos_map = {p.id: p for p in photos_res.scalars().all()}
        else:
            photos_map = {}

        enriched_results = []
        for res in results:
            photo_id = res.get("photo_id")
            if not photo_id or photo_id not in photos_map:
                continue
                
            photo = photos_map[photo_id]
            target_key = photo.watermark_s3_key or photo.s3_object_key
            
            # Generate 1 hour presigned URL
            url = await s3_client.generate_presigned_url(target_key, expiration=3600)
            
            res["url"] = url
            res["price_xof"] = unit_price
            if "original_key" in res:
                del res["original_key"]
            enriched_results.append(res)
                
        return {"results": enriched_results}
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {e}")

@router.post("/forget")
async def forget_faces(
    request: Request,
    competition_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Proxy pour oublier un visage pour une compétition.
    Accessible uniquement aux utilisateurs connectés.
    """
    try:
        # Log the biometric forget request
        audit_log = AuditLog(
            actor_type="user",
            actor_id=str(current_user.id),
            entity_type="competition",
            entity_id=str(competition_id),
            action="face_forget",
            metadata_json={"ip": request.client.host if request.client else "unknown"}
        )
        db.add(audit_log)
        await db.commit()
        content = await file.read(10 * 1024 * 1024 + 1)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_API_URL}/forget",
                data={"competition_id": competition_id},
                files={"file": (file.filename, content, file.content_type)},
                timeout=30.0
            )
            
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
            
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {e}")
