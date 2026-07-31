import uuid
from app.infrastructure.s3_client import s3_client

async def generate_upload_url(filename: str, content_type: str = "image/jpeg", is_watermark: bool = False) -> dict:
    """
    GÃ©nÃ¨re une URL prÃ©signÃ©e pour uploader un fichier directement sur S3/MinIO.
    """
    file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
    unique_id = str(uuid.uuid4())
    
    prefix = "watermarks" if is_watermark else "originals"
    object_key = f"{prefix}/{unique_id}.{file_extension}"
    
    url = await s3_client.generate_presigned_url(
        object_name=object_key,
        method='put_object',
        expiration=3600
    )
    
    return {
        "upload_url": url,
        "object_key": object_key
    }

async def generate_download_url(object_key: str, expiration: int = 3600) -> str:
    """
    GÃ©nÃ¨re une URL prÃ©signÃ©e pour lire/tÃ©lÃ©charger un fichier.
    """
    url = await s3_client.generate_presigned_url(
        object_name=object_key,
        method='get_object',
        expiration=expiration
    )
    return url
