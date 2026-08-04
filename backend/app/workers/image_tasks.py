import io
from PIL import Image, ImageDraw
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import update
from app.infrastructure.s3_client import s3_client
from app.modules.competitions.models import Photo, PhotoStatus
from app.core.config import settings

async def generate_watermark(ctx, photo_id: int, original_key: str, watermark_key: str):
    """
    TÃ¢che asynchrone Arq pour gÃ©nÃ©rer un filigrane.
    """
    try:
        # 1. Download original image
        async with s3_client.get_client() as client:
            response = await client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=original_key)
            image_data = await response['Body'].read()
        
        # 2. Process image with Pillow
        image = Image.open(io.BytesIO(image_data))
        
        # Resize for low-res (max 1024x1024)
        image.thumbnail((1024, 1024))
        
        # Add watermark text
        draw = ImageDraw.Draw(image)
        
        # 2.5 Query photographer name
        photographer_name = "ZoPic Studio"
        engine = create_async_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://") if settings.DATABASE_URL.startswith("postgresql://") else settings.DATABASE_URL)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            from sqlalchemy.future import select
            from app.modules.competitions.models import Photo, Epreuve, Competition
            from app.modules.auth.models import User
            query = select(User.full_name).join(Competition, Competition.photographer_id == User.id).join(Epreuve, Epreuve.competition_id == Competition.id).join(Photo, Photo.epreuve_id == Epreuve.id).where(Photo.id == photo_id)
            result = await session.execute(query)
            full_name = result.scalar_one_or_none()
            if full_name:
                photographer_name = full_name
        
        text = f"Aperçu — ZoPic Studio | {photographer_name}"
        
        # Simple watermark top-left (MVP)
        draw.text((20, 20), text, fill=(255, 255, 255, 180))
        
        # Save to buffer
        out_buffer = io.BytesIO()
        image.save(out_buffer, format="JPEG")
        out_buffer.seek(0)
        
        # 3. Upload watermark image
        async with s3_client.get_client() as client:
            await client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=watermark_key,
                Body=out_buffer.getvalue(),
                ContentType='image/jpeg'
            )
            
        # 4. Update Database
        engine = create_async_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://") if settings.DATABASE_URL.startswith("postgresql://") else settings.DATABASE_URL)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            stmt = update(Photo).where(Photo.id == photo_id).values(status=PhotoStatus.PROCESSED)
            await session.execute(stmt)
            await session.commit()
            
        await engine.dispose()
        return True
    except Exception as e:
        print(f"Error processing watermark for photo {photo_id}: {e}")
        engine = create_async_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://") if settings.DATABASE_URL.startswith("postgresql://") else settings.DATABASE_URL)
        async_session = async_sessionmaker(engine, expire_on_commit=False)
        async with async_session() as session:
            stmt = update(Photo).where(Photo.id == photo_id).values(status=PhotoStatus.FAILED)
            await session.execute(stmt)
            await session.commit()
        await engine.dispose()
        return False
