import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
import sys

async def main():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/orders/999/photos/1/download")
        print("Status:", res.status_code)
        print("Body:", res.json())

if __name__ == "__main__":
    asyncio.run(main())
