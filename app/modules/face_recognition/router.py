import os
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/faces", tags=["Face Recognition"])

AI_API_URL = os.getenv("AI_API_URL", "http://localhost:8001")

@router.post("/search")
async def search_faces(file: UploadFile = File(...)):
    """
    Proxy pour le worker IA. Envoie le selfie au worker pour extraction
    et recherche dans Qdrant.
    """
    try:
        content = await file.read()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_API_URL}/search",
                files={"file": (file.filename, content, file.content_type)},
                timeout=30.0
            )
            
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
            
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {e}")
