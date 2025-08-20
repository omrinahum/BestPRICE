# backend/schemas/offer_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OfferBase(BaseModel):
    title: str
    price: float
    currency: str
    url: str
    source: str
    brand: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None
    shipping_cost: Optional[float] = None

class OfferCreate(OfferBase):
    search_id: int

class OfferResponse(OfferBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
