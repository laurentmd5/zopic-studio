import asyncio
import os
import time
from datetime import datetime, timezone, timedelta
from qdrant_client import AsyncQdrantClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.modules.competitions.models import Competition, CompetitionStatus
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./zopic.db")

async def cleanup():
    engine = create_async_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    qdrant = AsyncQdrantClient(url=QDRANT_URL)
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
    logger.info(f"Checking for archived/completed competitions before {cutoff_date}...")
    
    async with SessionLocal() as db:
        # Find competitions that are archived (or if we had a closed status, we could use that)
        # Assuming ARCHIVED is the status for closed competitions
        result = await db.execute(
            select(Competition).where(
                Competition.status == CompetitionStatus.ARCHIVED
            )
        )
        competitions = result.scalars().all()
        
        for comp in competitions:
            # Simplification: we use created_at or date as reference if no closed_at exists
            if comp.date and comp.date.replace(tzinfo=timezone.utc) < cutoff_date:
                collection_name = f"faces_v1_{comp.id}"
                if await qdrant.collection_exists(collection_name):
                    logger.info(f"Deleting collection {collection_name} for competition {comp.id}...")
                    await qdrant.delete_collection(collection_name)
                    
    logger.info("Cleanup finished.")

if __name__ == "__main__":
    asyncio.run(cleanup())
