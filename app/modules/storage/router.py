from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.modules.storage import service

router = APIRouter(prefix="/storage", tags=["Storage"])

class UploadUrlRequest(BaseModel):
    filename: str
    content_type: str = "image/jpeg"
    is_watermark: bool = False

class UploadUrlResponse(BaseModel):
    upload_url: str
    object_key: str

@router.post("/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(request: UploadUrlRequest):
    """
    RÃ©cupÃ¨re un lien prÃ©signÃ© pour uploader directement un fichier sur MinIO/S3.
    (Note: En production, on ajouterait une dÃ©pendance de sÃ©curitÃ© pour vÃ©rifier que le user est authentifiÃ©)
    """
    try:
        result = await service.generate_upload_url(
            filename=request.filename,
            content_type=request.content_type,
            is_watermark=request.is_watermark
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
