from qdrant_client import AsyncQdrantClient
from app.core.config import settings

class QdrantWrapper:
    def __init__(self):
        self.client = AsyncQdrantClient(url=settings.QDRANT_URL)

    async def create_collection_if_not_exists(self, collection_name: str, vector_size: int = 512):
        # In MVP InsightFace typically outputs 512-d vectors (e.g. arcface)
        collections = await self.client.get_collections()
        if collection_name not in [c.name for c in collections.collections]:
            from qdrant_client.http import models
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
            
    async def search(self, collection_name: str, vector: list[float], limit: int = 10):
        return await self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

qdrant_client_wrapper = QdrantWrapper()
