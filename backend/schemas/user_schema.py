# backend/schemas/user_schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class WatchlistItemBase(BaseModel):
    product_title: str
    product_url: Optional[str] = None


class WatchlistItemCreate(WatchlistItemBase):
    offer_id: Optional[int] = None  # can link to existing offer


class WatchlistItemResponse(WatchlistItemBase):
    id: int
    user_id: int
    offer_id: Optional[int] = None
    current_price: Optional[float] = None
    source: Optional[str] = None
    product_image_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
