import aioboto3
from typing import Optional
from app.core.config import settings

class S3Client:
    def __init__(self):
        self.session = aioboto3.Session()

    def get_client(self):
        return self.session.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )
    
    async def generate_presigned_url(self, object_name: str, expiration: int = 3600, method: str = 'get_object') -> str:
        async with self.get_client() as client:
            response = await client.generate_presigned_url(
                ClientMethod=method,
                Params={
                    'Bucket': settings.S3_BUCKET_NAME,
                    'Key': object_name
                },
                ExpiresIn=expiration
            )
            return response

s3_client = S3Client()
