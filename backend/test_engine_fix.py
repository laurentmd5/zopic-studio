import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

print("Set loop policy")

from sqlalchemy.ext.asyncio import create_async_engine
engine = create_async_engine('sqlite+aiosqlite:///:memory:')
print("Engine created successfully")
