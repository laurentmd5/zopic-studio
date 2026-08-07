import os
from arq.connections import RedisSettings
from app.modules.downloads.handlers import handle_payment_completed
from app.modules.athletes.handlers import update_athlete_statistics
from app.modules.payments.events import PaymentCompletedEvent
from pydantic import BaseModel
from arq.cron import cron
import json
from datetime import datetime, timezone, timedelta
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from app.core.config import settings
from qdrant_client import AsyncQdrantClient

logger = logging.getLogger(__name__)

async def arq_handle_payment_completed(ctx, event_data: dict):
    event = PaymentCompletedEvent(**event_data)
    await handle_payment_completed(event)

async def arq_update_athlete_statistics(ctx, event_data: dict):
    event = PaymentCompletedEvent(**event_data)
    await update_athlete_statistics(event)

async def process_outbox_events(ctx):
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from sqlalchemy.future import select
    from app.core.config import settings
    from app.core.outbox import OutboxEvent
    
    # 1. Connect to DB
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    # 2. Fetch PENDING events
    async with SessionLocal() as db:
        result = await db.execute(
            select(OutboxEvent).where(OutboxEvent.status == "PENDING").order_by(OutboxEvent.created_at).limit(50)
        )
        events = result.scalars().all()
        
        if not events:
            return
            
        logger.info(f"Found {len(events)} PENDING outbox events to process.")
        
        # 3. Publish to ARQ
        redis = ctx['redis']
        for evt in events:
            try:
                if evt.event_type == "PaymentCompletedEvent":
                    await redis.enqueue_job("arq_handle_payment_completed", evt.payload)
                    await redis.enqueue_job("arq_update_athlete_statistics", evt.payload)
                else:
                    logger.warning(f"No ARQ handlers mapped for event type {evt.event_type}")
                
                # Mark as PROCESSED
                evt.status = "PROCESSED"
                evt.processed_at = datetime.now(timezone.utc)
            except Exception as e:
                logger.error(f"Failed to process outbox event {evt.id}: {e}")
                evt.status = "FAILED"
                
        await db.commit()
    
    await engine.dispose()

async def arq_cleanup_biometrics(ctx):
    from app.modules.competitions.models import Competition, CompetitionStatus
    
    logger.info("Starting scheduled biometric cleanup...")
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    # Timeout and retry might be needed for qdrant client in production
    qdrant = AsyncQdrantClient(url=os.getenv("QDRANT_URL", "http://localhost:6333"))
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
    logger.info(f"Checking for archived competitions before {cutoff_date}...")
    
    async with SessionLocal() as db:
        result = await db.execute(
            select(Competition).where(
                Competition.status == CompetitionStatus.ARCHIVED
            )
        )
        competitions = result.scalars().all()
        
        for comp in competitions:
            if comp.date and comp.date.replace(tzinfo=timezone.utc) < cutoff_date:
                collection_name = f"faces_v1_{comp.id}"
                if await qdrant.collection_exists(collection_name):
                    logger.info(f"Deleting collection {collection_name} for competition {comp.id}...")
                    await qdrant.delete_collection(collection_name)
                    
    await engine.dispose()
    logger.info("Biometric cleanup finished.")

class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    functions = [
        arq_handle_payment_completed,
        arq_update_athlete_statistics,
        arq_cleanup_biometrics
    ]
    cron_jobs = [
        cron(process_outbox_events, second={0, 10, 20, 30, 40, 50}),
        cron(arq_cleanup_biometrics, hour=3, minute=0)
    ]
