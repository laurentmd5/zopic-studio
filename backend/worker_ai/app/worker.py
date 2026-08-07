import os
import uuid
import aioboto3
from arq.connections import RedisSettings
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
import logging

logger = logging.getLogger(__name__)

from app.services.face_analyzer import face_analyzer

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "zopic-studio")

async def extract_faces(ctx, photo_id: int, event_id: int, album_id: int, original_key: str):
    logger.info(f"Extraction des visages pour la photo {photo_id}...")
    
    try:
        # 1. Download image from MinIO
        session = aioboto3.Session()
        async with session.client(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name="us-east-1"
        ) as s3:
            response = await s3.get_object(Bucket=S3_BUCKET_NAME, Key=original_key)
            image_data = await response['Body'].read()
            
        # 2. Extract faces
        embeddings = face_analyzer.extract_faces(image_data)
        
        if not embeddings:
            logger.info(f"Aucun visage detecte dans la photo {photo_id}.")
            return False
            
        logger.info(f"{len(embeddings)} visage(s) detecte(s) dans la photo {photo_id}.")
        
        # 3. Store in Qdrant
        qdrant = AsyncQdrantClient(url=QDRANT_URL)
        
        import time
        from datetime import datetime, timezone
        
        points = []
        for emb in embeddings:
            point_id = str(uuid.uuid4())
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=emb,
                    payload={
                        "photo_id": photo_id,
                        "event_id": event_id,
                        "album_id": album_id,
                        "original_key": original_key,
                        "created_at": int(time.time()),
                        "model_version": "v1.0"
                    }
                )
            )
            
        collection_name = f"faces_v1_{event_id}"
        
        # Ensure collection exists
        if not await qdrant.collection_exists(collection_name):
            from qdrant_client.http import models as qmodels
            await qdrant.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(size=len(embeddings[0]), distance=qmodels.Distance.COSINE)
            )

        await qdrant.upsert(
            collection_name=collection_name,
            points=points
        )
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction de la photo {photo_id}", exc_info=True)
        return False

import zipfile
import io
import aiohttp

async def generate_zip(ctx, archive_id: int, s3_keys: list[str], callback_url: str, callback_secret: str):
    logger.info(f"Generation de l'archive ZIP {archive_id} pour {len(s3_keys)} fichiers...")
    
    try:
        session = aioboto3.Session()
        zip_buffer = io.BytesIO()
        
        async with session.client(
            's3',
            endpoint_url=S3_ENDPOINT_URL,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
            region_name="us-east-1"
        ) as s3:
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for key in s3_keys:
                    try:
                        response = await s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
                        file_data = await response['Body'].read()
                        filename = key.split('/')[-1]
                        zip_file.writestr(filename, file_data)
                    except Exception as e:
                        logger.error(f"Erreur lors du telechargement d'un fichier pour l'archive {archive_id}", exc_info=True)
            
            zip_buffer.seek(0)
            zip_key = f"archives/archive_{archive_id}.zip"
            
            await s3.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=zip_key,
                Body=zip_buffer.getvalue(),
                ContentType='application/zip'
            )
            
            # Notify backend
            async with aiohttp.ClientSession() as http_session:
                await http_session.post(
                    callback_url,
                    json={"status": "COMPLETED", "s3_object_key": zip_key, "size": len(zip_buffer.getvalue())},
                    headers={"X-Archive-Secret": callback_secret}
                )
                
            logger.info(f"Archive {archive_id} generee avec succes.")
            return True
            
    except Exception as e:
        logger.error(f"Erreur lors de la generation de l'archive {archive_id}", exc_info=True)
        async with aiohttp.ClientSession() as http_session:
            await http_session.post(
                callback_url,
                json={"status": "FAILED"},
                headers={"X-Archive-Secret": callback_secret}
            )
        return False

class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(REDIS_URL)
    functions = [extract_faces, generate_zip]
    queue_name = 'arq:ai_queue' # On utilise une queue différente pour l'IA
