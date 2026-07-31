from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from app.modules.events.models import PhotoStatus

# Photo Schemas
class PhotoBase(BaseModel):
    s3_object_key: str

class PhotoCreate(PhotoBase):
    pass

class PhotoResponse(PhotoBase):
    id: int
    album_id: int
    watermark_s3_key: Optional[str]
    status: PhotoStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Album Schemas
class AlbumBase(BaseModel):
    name: str

class AlbumCreate(AlbumBase):
    pass

class AlbumResponse(AlbumBase):
    id: int
    event_id: int
    created_at: datetime
    photos: List[PhotoResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

# Event Schemas
class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    date: datetime
    is_public: bool = True
    access_code: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    photographer_id: int
    created_at: datetime
    albums: List[AlbumResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
