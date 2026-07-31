import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infrastructure.qdrant_client_wrapper import qdrant_client_wrapper

async def init():
    print("Initialisation Qdrant...")
    try:
        await qdrant_client_wrapper.create_collection_if_not_exists("faces", 512)
        collections = await qdrant_client_wrapper.client.get_collections()
        print(f"Connexion Qdrant OK. Collections existantes : {collections.collections}")
    except Exception as e:
        print(f"Erreur de connexion a Qdrant : {e}")

if __name__ == "__main__":
    asyncio.run(init())
