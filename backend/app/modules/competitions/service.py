from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.modules.competitions.models import Competition, Epreuve, Photo, PhotoStatus
from app.modules.competitions import schemas
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings

async def create_competition(db: AsyncSession, competition_data: schemas.CompetitionCreate, user_id: int) -> Competition:
    db_competition = Competition(
        name=competition_data.name,
        description=competition_data.description,
        date=competition_data.date,
        photographer_id=user_id,
        is_public=competition_data.is_public,
        access_code=competition_data.access_code
    )
    db.add(db_competition)
    await db.commit()
    await db.refresh(db_competition)
    return db_competition

async def get_competitions(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Competition).where(Competition.is_public == True).offset(skip).limit(limit))
    return result.scalars().all()

async def get_epreuve(db: AsyncSession, epreuve_id: int):
    result = await db.execute(select(Epreuve).where(Epreuve.id == epreuve_id))
    return result.scalars().first()

async def get_competition(db: AsyncSession, competition_id: int):
    result = await db.execute(select(Competition).options(selectinload(Competition.epreuves)).where(Competition.id == competition_id))
    return result.scalars().first()

async def create_epreuve(db: AsyncSession, competition_id: int, epreuve_data: schemas.EpreuveCreate) -> Epreuve:
    db_epreuve = Epreuve(
        competition_id=competition_id,
        name=epreuve_data.name
    )
    db.add(db_epreuve)
    await db.commit()
    await db.refresh(db_epreuve)
    return db_epreuve

async def add_photo(db: AsyncSession, epreuve_id: int, photo_data: schemas.PhotoCreate) -> Photo:
    # 0. Check Quota
    album_result = await db.execute(select(Epreuve).where(Epreuve.id == epreuve_id))
    db_epreuve = album_result.scalars().first()
    
    if db_epreuve:
        comp_res = await db.execute(select(Competition).where(Competition.id == db_epreuve.competition_id))
        db_comp = comp_res.scalars().first()
        
        if db_comp:
            from app.modules.subscriptions.models import StorageUsage, Subscription, Plan
            usage_res = await db.execute(select(StorageUsage).where(StorageUsage.user_id == db_comp.photographer_id))
            usage = usage_res.scalars().first()
            
            sub_res = await db.execute(select(Subscription).where(Subscription.user_id == db_comp.photographer_id, Subscription.is_active == True))
            active_sub = sub_res.scalars().first()
            
            plan_limit_bytes = 1 * 1024 * 1024 * 1024 # 1 Go by default
            if active_sub:
                plan_res = await db.execute(select(Plan).where(Plan.id == active_sub.plan_id))
                plan = plan_res.scalars().first()
                if plan:
                    plan_limit_bytes = plan.storage_limit_gb * 1024 * 1024 * 1024
            
            used_bytes = usage.used_bytes if usage else 0
            file_size = photo_data.file_size_bytes or 5 * 1024 * 1024 # 5 MB fallback
            
            if used_bytes + file_size > plan_limit_bytes:
                from fastapi import HTTPException
                raise HTTPException(status_code=413, detail="Vous avez atteint votre limite de stockage. Passez à un plan supérieur pour continuer.")
            
            # Update usage directly
            if not usage:
                usage = StorageUsage(user_id=db_comp.photographer_id, used_bytes=file_size)
                db.add(usage)
            else:
                usage.used_bytes += file_size
            
    # 1. Enregistrer la photo en base avec statut UPLOADED
    watermark_key = photo_data.s3_object_key.replace("originals/", "watermarks/")
    db_photo = Photo(
        epreuve_id=epreuve_id,
        s3_object_key=photo_data.s3_object_key,
        watermark_s3_key=watermark_key,
        status=PhotoStatus.UPLOADED
    )
    db.add(db_photo)
    await db.commit()
    await db.refresh(db_photo)
    # Fetch epreuve to get competition_id
    album_result = await db.execute(select(Epreuve).where(Epreuve.id == epreuve_id))
    db_epreuve = album_result.scalars().first()
    
    # 2. Déclencher la tâche asynchrone Arq (Filigrane)
    redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    await redis.enqueue_job(
        'generate_watermark',
        db_photo.id,
        db_photo.s3_object_key,
        db_photo.watermark_s3_key
    )
    
    # 3. Déclencher la tâche d'extraction IA sur la queue spécifique
    if db_epreuve:
        await redis.enqueue_job(
            'extract_faces',
            db_photo.id,
            db_epreuve.competition_id,
            epreuve_id,
            db_photo.s3_object_key,
            _queue_name='arq:ai_queue'
        )
    
    return db_photo
