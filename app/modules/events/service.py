from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.events.models import Event, Album, Photo, PhotoStatus
from app.modules.events import schemas
from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings

async def create_event(db: AsyncSession, event_data: schemas.EventCreate, user_id: int) -> Event:
    db_event = Event(
        name=event_data.name,
        description=event_data.description,
        date=event_data.date,
        photographer_id=user_id,
        is_public=event_data.is_public,
        access_code=event_data.access_code
    )
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def get_events(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Event).offset(skip).limit(limit))
    return result.scalars().all()

async def get_event(db: AsyncSession, event_id: int):
    result = await db.execute(select(Event).where(Event.id == event_id))
    return result.scalars().first()

async def create_album(db: AsyncSession, event_id: int, album_data: schemas.AlbumCreate) -> Album:
    db_album = Album(
        event_id=event_id,
        name=album_data.name
    )
    db.add(db_album)
    await db.commit()
    await db.refresh(db_album)
    return db_album

async def add_photo(db: AsyncSession, album_id: int, photo_data: schemas.PhotoCreate) -> Photo:
    # 1. Enregistrer la photo en base avec statut UPLOADED
    watermark_key = photo_data.s3_object_key.replace("originals/", "watermarks/")
    db_photo = Photo(
        album_id=album_id,
        s3_object_key=photo_data.s3_object_key,
        watermark_s3_key=watermark_key,
        status=PhotoStatus.UPLOADED
    )
    db.add(db_photo)
    await db.commit()
    await db.refresh(db_photo)
    # Fetch album to get event_id
    album_result = await db.execute(select(Album).where(Album.id == album_id))
    db_album = album_result.scalars().first()
    
    # 2. DÃ©clencher la tÃ¢che asynchrone Arq (Filigrane)
    redis = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    await redis.enqueue_job(
        'generate_watermark',
        db_photo.id,
        db_photo.s3_object_key,
        db_photo.watermark_s3_key
    )
    
    # 3. DÃ©clencher la tÃ¢che d'extraction IA sur la queue spÃ©cifique
    if db_album:
        await redis.enqueue_job(
            'extract_faces',
            db_photo.id,
            db_album.event_id,
            album_id,
            db_photo.s3_object_key,
            _queue_name='arq:ai_queue'
        )
    
    return db_photo
