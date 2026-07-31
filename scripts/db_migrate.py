import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from alembic.config import Config
from alembic import command
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.core.database import Base
# Make sure models are imported so Base has them
from app.modules.auth import models

async def migrate():
    # Enforce asyncpg dialect for Alembic if not in URL
    url = settings.DATABASE_URL
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")

    engine = create_async_engine(url)
    
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version');")
        )
        has_alembic = result.scalar()
        
        if not has_alembic:
            print("Premier deploiement : Creation des tables via SQLAlchemy...")
            await conn.run_sync(Base.metadata.create_all)
            print("Stamping alembic head...")
            alembic_cfg = Config("alembic.ini")
            command.stamp(alembic_cfg, "head")
        else:
            print("Deploiements suivants : Execution de alembic upgrade head...")
            alembic_cfg = Config("alembic.ini")
            command.upgrade(alembic_cfg, "head")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
