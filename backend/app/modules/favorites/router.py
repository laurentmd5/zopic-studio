from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from pydantic import BaseModel

from app.core.database import get_db
from app.modules.competitions.models import Favorite, Photo
from app.modules.auth.service import get_current_user_optional
from app.modules.auth.models import User

router = APIRouter(prefix="/api/v1/favorites", tags=["Favorites"])

class FavoriteResponse(BaseModel):
    id: int
    photo_id: int
    session_id: Optional[str]
    user_id: Optional[int]
    
    class Config:
        from_attributes = True

@router.post("/{photo_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    photo_id: int,
    x_session_id: Optional[str] = Header(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    if not current_user and not x_session_id:
        raise HTTPException(status_code=400, detail="session_id or authenticated user required")

    # Verify photo exists
    result = await db.execute(select(Photo).filter(Photo.id == photo_id))
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Check if already favorited
    query = select(Favorite).filter(Favorite.photo_id == photo_id)
    if current_user:
        query = query.filter(Favorite.user_id == current_user.id)
    else:
        query = query.filter(Favorite.session_id == x_session_id)
        
    existing_result = await db.execute(query)
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        return existing

    new_fav = Favorite(
        photo_id=photo_id,
        user_id=current_user.id if current_user else None,
        session_id=x_session_id if not current_user else None
    )
    
    db.add(new_fav)
    await db.commit()
    await db.refresh(new_fav)
    return new_fav

@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    photo_id: int,
    x_session_id: Optional[str] = Header(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    if not current_user and not x_session_id:
        raise HTTPException(status_code=400, detail="session_id or authenticated user required")

    query = select(Favorite).filter(Favorite.photo_id == photo_id)
    if current_user:
        query = query.filter(Favorite.user_id == current_user.id)
    else:
        query = query.filter(Favorite.session_id == x_session_id)
        
    result = await db.execute(query)
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
        
    await db.delete(favorite)
    await db.commit()
    return None

@router.get("/", response_model=List[FavoriteResponse])
async def get_favorites(
    x_session_id: Optional[str] = Header(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    if not current_user and not x_session_id:
        raise HTTPException(status_code=400, detail="session_id or authenticated user required")

    query = select(Favorite)
    if current_user:
        query = query.filter(Favorite.user_id == current_user.id)
    else:
        query = query.filter(Favorite.session_id == x_session_id)
        
    result = await db.execute(query)
    favorites = result.scalars().all()
    return favorites
