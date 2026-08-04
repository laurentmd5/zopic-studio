print("Starting check_db")
from app.core.config import settings
print("Config loaded")
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
print("Imports done")

print(f"DATABASE_URL is {settings.DATABASE_URL}")

try:
    engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
    print("Engine created")
except Exception as e:
    print(f"Engine failed: {e}")

try:
    session_maker = async_sessionmaker(bind=engine)
    print("Session maker created")
except Exception as e:
    print(f"Session maker failed: {e}")

print("Done")
