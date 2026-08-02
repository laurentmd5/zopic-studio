from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from app.modules.competitions.models import PhotoStatus

# Photo Schemas
class PhotoBase(BaseModel):
    s3_object_key: str

class PhotoCreate(PhotoBase):
    pass

class PhotoResponse(PhotoBase):
    id: int
    epreuve_id: int
    watermark_s3_key: Optional[str]
    status: PhotoStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Epreuve Schemas
class EpreuveBase(BaseModel):
    name: str

class EpreuveCreate(EpreuveBase):
    pass

class EpreuveResponse(EpreuveBase):
    id: int
    competition_id: int
    created_at: datetime
    photos: List[PhotoResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# Competition Schemas
class CompetitionBase(BaseModel):
    name: str
    description: Optional[str] = None
    date: datetime
    is_public: bool = True
    access_code: Optional[str] = None
    settings: Optional[dict] = {}

class CompetitionCreate(CompetitionBase):
    pass

class CompetitionResponse(CompetitionBase):
    id: int
    photographer_id: int
    created_at: datetime
    epreuves: List[EpreuveResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
