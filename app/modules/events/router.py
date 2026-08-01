from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.modules.events import schemas, service
from app.core.database import get_db

# Note: In a real application, we would use a dependency like `get_current_user`
# For MVP simplicity, we'll hardcode a fake user_id or accept it in headers/query.
# Let's mock a user_id dependency for now.
async def get_current_user_id() -> int:
    return 1 # Fake user ID for MVP photographer

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/", response_model=schemas.EventResponse)
async def create_event(
    event: schemas.EventCreate, 
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return await service.create_event(db, event, user_id)

@router.get("/", response_model=List[schemas.EventResponse])
async def read_events(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await service.get_events(db, skip=skip, limit=limit)

@router.get("/{event_id}", response_model=schemas.EventResponse)
async def read_event(event_id: int, access_code: str = None, db: AsyncSession = Depends(get_db)):
    event = await service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if not event.is_public:
        if not event.access_code or event.access_code != access_code:
            raise HTTPException(status_code=403, detail="Code d'accès invalide ou manquant")
            
    return event

@router.post("/{event_id}/albums", response_model=schemas.AlbumResponse)
async def create_album(event_id: int, album: schemas.AlbumCreate, db: AsyncSession = Depends(get_db)):
    # VÃ©rifier si l'Ã©vÃ©nement existe
    event = await service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return await service.create_album(db, event_id, album)

@router.post("/albums/{album_id}/photos", response_model=schemas.PhotoResponse)
async def add_photo_to_album(album_id: int, photo: schemas.PhotoCreate, db: AsyncSession = Depends(get_db)):
    # Ajouter la photo (qui a Ã©tÃ© uploadÃ©e via Presigned URL) Ã  la BDD
    return await service.add_photo(db, album_id, photo)
