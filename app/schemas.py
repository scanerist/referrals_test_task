from typing import Optional, List

from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class TokenData(BaseModel):
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class ReferalCodeCreate(BaseModel):
    expires_at: datetime

class ReferalCoderesponse(BaseModel):
    code: str
    expires_at: datetime

class ReferalResponse(BaseModel):
    id: int
    referer_id: int
    refered_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True