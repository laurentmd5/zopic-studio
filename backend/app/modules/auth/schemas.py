from pydantic import BaseModel, ConfigDict
from typing import Optional

class OTPRequest(BaseModel):
    phone_number: str

class OTPVerify(BaseModel):
    phone_number: str
    code: str

class Token(BaseModel):
    access_token: str
    token_type: str

class PhotographerProfileBase(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    logo_url: Optional[str] = None
    payment_number: Optional[str] = None

class PhotographerProfileResponse(PhotographerProfileBase):
    id: int
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class PhotographerProfileUpdate(PhotographerProfileBase):
    pass

class UserResponse(BaseModel):
    id: int
    phone_number: str
    is_photographer: bool
    photographer_profile: Optional[PhotographerProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)
