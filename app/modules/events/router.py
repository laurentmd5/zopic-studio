from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.modules.events import schemas, service
from app.core.database import get_db
from app.modules.auth.service import get_current_user
from app.modules.auth.models import User

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("/", response_model=schemas.EventResponse)
async def create_event(
    event: schemas.EventCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_photographer:
        raise HTTPException(status_code=403, detail="Only photographers can create events")
    return await service.create_event(db, event, current_user.id)

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
