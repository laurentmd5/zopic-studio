import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from qdrant_client import AsyncQdrantClient

from app.services.face_analyzer import face_analyzer

app = FastAPI(title="ZoPic Studio - AI Worker API")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
AI_INTERNAL_TOKEN = os.getenv("AI_INTERNAL_TOKEN", "changeme")
FACE_MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", "0.85"))

async def verify_token(ai_internal_token: str = Header(..., alias="X-AI-Internal-Token")):
    if ai_internal_token != AI_INTERNAL_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid internal token")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "worker-ai"}

from fastapi import Form
@app.post("/search", dependencies=[Depends(verify_token)])
async def search_faces(
    competition_id: int = Form(...),
    file: UploadFile = File(...)
):
    """
    Reçoit un selfie, extrait l'embedding du visage principal,
    et recherche les photos similaires dans Qdrant pour la compétition donnée.
    """
    try:
        content = await file.read()
        embeddings = face_analyzer.extract_faces(content)
        
        if not embeddings:
            raise HTTPException(status_code=400, detail="Aucun visage detecte sur le selfie.")
            
        # On prend le premier visage (le plus proéminent)
        main_face_embedding = embeddings[0]
        
        # Recherche dans Qdrant
        qdrant = AsyncQdrantClient(url=QDRANT_URL)
        collection_name = f"faces_v1_{competition_id}"
        
        # Verify collection exists
        if not await qdrant.collection_exists(collection_name):
            return {"results": []}
            
        search_result = await qdrant.search(
            collection_name=collection_name,
            query_vector=main_face_embedding,
            limit=20, # On renvoie les 20 meilleures correspondances
            score_threshold=FACE_MATCH_THRESHOLD # Seuil de similarité (Cosine)
        )
        
        # Format the response
        results = []
        for hit in search_result:
            results.append({
                "score": hit.score,
                "photo_id": hit.payload.get("photo_id"),
                "event_id": hit.payload.get("event_id"),
                "album_id": hit.payload.get("album_id"),
                "original_key": hit.payload.get("original_key")
            })
            
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/forget", dependencies=[Depends(verify_token)])
async def forget_faces(
    competition_id: int = Form(...),
    file: UploadFile = File(...)
):
    """
    Extrait l'embedding du selfie et supprime les points correspondants
    dans Qdrant pour la compétition donnée.
    """
    try:
        content = await file.read()
        embeddings = face_analyzer.extract_faces(content)
        
        if not embeddings:
            raise HTTPException(status_code=400, detail="Aucun visage detecte sur le selfie.")
            
        main_face_embedding = embeddings[0]
        qdrant = AsyncQdrantClient(url=QDRANT_URL)
        collection_name = f"faces_v1_{competition_id}"
        
        if not await qdrant.collection_exists(collection_name):
            return {"deleted_faces": 0}
            
        search_result = await qdrant.search(
            collection_name=collection_name,
            query_vector=main_face_embedding,
            limit=1000,
            score_threshold=FACE_MATCH_THRESHOLD
        )
        
        point_ids = [hit.id for hit in search_result]
        if point_ids:
            from qdrant_client.http import models as qmodels
            await qdrant.delete(
                collection_name=collection_name,
                points_selector=qmodels.PointIdsList(points=point_ids)
            )
            
        return {"deleted_faces": len(point_ids)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
