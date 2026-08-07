from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.modules.storage import service
from app.modules.auth.models import User
from app.modules.auth.service import get_current_user

router = APIRouter(prefix="/storage", tags=["Storage"])

class UploadUrlRequest(BaseModel):
    filename: str
    content_type: str = "image/jpeg"
    is_watermark: bool = False

class UploadUrlResponse(BaseModel):
    upload_url: str
    object_key: str

@router.post("/upload-url", response_model=UploadUrlResponse)
async def get_upload_url(
    request: UploadUrlRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Récupère un lien présigné pour uploader directement un fichier sur MinIO/S3.
    Réservé aux photographes.
    """
    if not current_user.is_photographer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès réservé aux photographes.")
    try:
        result = await service.generate_upload_url(
            filename=request.filename,
            content_type=request.content_type,
            is_watermark=request.is_watermark
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/download-url")
async def get_download_url(
    object_key: str,
    current_user: User = Depends(get_current_user)
):
    """
    Récupère un lien présigné pour lire/télécharger un fichier sur S3/MinIO.
    """
    try:
        url = await service.generate_download_url(object_key)
        return {"download_url": url}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
