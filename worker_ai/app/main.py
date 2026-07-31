import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from qdrant_client import AsyncQdrantClient

from app.services.face_analyzer import face_analyzer

app = FastAPI(title="ZoPic Studio - AI Worker API")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "worker-ai"}

@app.post("/search")
async def search_faces(file: UploadFile = File(...)):
    """
    ReÃ§oit un selfie, extrait l'embedding du visage principal,
    et recherche les photos similaires dans Qdrant.
    """
    try:
        content = await file.read()
        embeddings = face_analyzer.extract_faces(content)
        
        if not embeddings:
            raise HTTPException(status_code=400, detail="Aucun visage detecte sur le selfie.")
            
        # On prend le premier visage (le plus proÃ©minent)
        main_face_embedding = embeddings[0]
        
        # Recherche dans Qdrant
        qdrant = AsyncQdrantClient(url=QDRANT_URL)
        search_result = await qdrant.search(
            collection_name="faces",
            query_vector=main_face_embedding,
            limit=20, # On renvoie les 20 meilleures correspondances
            score_threshold=0.6 # Seuil de similaritÃ© (Cosine)
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
