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
from app.modules.auth import models as auth_models
from app.modules.events import models as events_models

async def check_and_create_tables():
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
        
        print("Verification et creation des tables manquantes via SQLAlchemy...")
        await conn.run_sync(Base.metadata.create_all)
        
        if not has_alembic:
            
    await engine.dispose()
    return has_alembic

def main():
    has_alembic = asyncio.run(check_and_create_tables())
    
    alembic_cfg = Config("alembic.ini")
    if not has_alembic:
        print("Stamping alembic head...")
        command.stamp(alembic_cfg, "head")
    else:
        print("Deploiements suivants : Execution de alembic upgrade head...")
        command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    main()
