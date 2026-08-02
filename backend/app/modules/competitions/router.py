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
async def create_epreuve(competition_id: int, epreuve: schemas.EpreuveCreate, db: AsyncSession = Depends(get_db)):
    # VÃ©rifier si l'Ã©vÃ©nement existe
    competition = await service.get_competition(db, competition_id)
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")
    return await service.create_epreuve(db, competition_id, epreuve)

@router.post("/epreuves/{epreuve_id}/photos", response_model=schemas.PhotoResponse)
async def add_photo_to_album(epreuve_id: int, photo: schemas.PhotoCreate, db: AsyncSession = Depends(get_db)):
    # Ajouter la photo (qui a Ã©tÃ© uploadÃ©e via Presigned URL) Ã  la BDD
    return await service.add_photo(db, epreuve_id, photo)
