from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.modules.competitions import schemas, service
from app.core.database import get_db
from app.modules.auth.service import get_current_user
from app.modules.auth.models import User

router = APIRouter(prefix="/competitions", tags=["Events"])

@router.post("/", response_model=schemas.CompetitionResponse)
async def create_competition(
    competition: schemas.CompetitionCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_photographer:
        raise HTTPException(status_code=403, detail="Only photographers can create competitions")
    return await service.create_competition(db, competition, current_user.id)

@router.get("/", response_model=List[schemas.CompetitionResponse])
async def read_events(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await service.get_competitions(db, skip=skip, limit=limit)

@router.get("/{competition_id}", response_model=schemas.CompetitionResponse)
async def read_event(competition_id: int, access_code: str = None, db: AsyncSession = Depends(get_db)):
    competition = await service.get_competition(db, competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    
    if not competition.is_public:
        if not competition.access_code or competition.access_code != access_code:
            raise HTTPException(status_code=403, detail="Code d'accès invalide ou manquant")
            
    return competition

@router.post("/{competition_id}/epreuves", response_model=schemas.EpreuveResponse)
async def create_epreuve(
    competition_id: int, 
    epreuve: schemas.EpreuveCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    competition = await service.get_competition(db, competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    if competition.photographer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this competition")
    return await service.create_epreuve(db, competition_id, epreuve)

@router.post("/epreuves/{epreuve_id}/photos", response_model=schemas.PhotoResponse)
async def add_photo_to_album(
    epreuve_id: int, 
    photo: schemas.PhotoCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Retrieve the epreuve to check the competition's photographer
    epreuve = await service.get_epreuve(db, epreuve_id)
    if not epreuve:
        raise HTTPException(status_code=404, detail="Epreuve not found")
    
    competition = await service.get_competition(db, epreuve.competition_id)
    if not competition or competition.photographer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add photos here")
        
    return await service.add_photo(db, epreuve_id, photo)

@router.put("/{competition_id}/packs", response_model=schemas.CompetitionResponse)
async def update_competition_packs(
    competition_id: int, 
    packs_update: schemas.CompetitionPacksUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    competition = await service.get_competition(db, competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    if competition.photographer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this competition")
        
    competition.packs_enabled = packs_update.packs_enabled
    # Convert Pydantic models to dict for JSON serialization
    competition.packs = [pack.model_dump() for pack in packs_update.packs]
    
    await db.commit()
    return await service.get_competition(db, competition_id)

@router.get("/{competition_id}/packs")
async def get_competition_packs(competition_id: int, db: AsyncSession = Depends(get_db)):
    competition = await service.get_competition(db, competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return {
        "packs_enabled": competition.packs_enabled,
        "packs": competition.packs or []
    }
