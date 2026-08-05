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
from app.modules.competitions import models as competitions_models
from app.modules.payments import models as payments_models
from app.modules.subscriptions import models as subscriptions_models
from app.modules.athletes import models as athletes_models
from app.modules.downloads import models as downloads_models
from app.modules.archives import models as archives_models
from app.modules.audit import models as audit_models

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
        
        # MVP: Drop old tables to recreate them with phone_number
        print("Nettoyage des anciennes tables Auth pour migration email -> phone_number...")
        await conn.execute(text("DROP TABLE IF EXISTS payouts CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS photo_sales CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS order_items CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS orders CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS subscriptions CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS storage_usage CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS photographer_profiles CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS otp_codes CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS events CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS albums CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS photos CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        
        print("Verification et creation des tables manquantes via SQLAlchemy...")
        await conn.run_sync(Base.metadata.create_all)
        

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
