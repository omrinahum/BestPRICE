# backend/schemas/offer_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class OfferBase(BaseModel):
    title: str
    last_price: Decimal
    currency: str
    url: str
    source: str
    source_offer_id: str
    seller: Optional[str] = None
    image_url: Optional[str] = None
    rating: Optional[float] = None

class OfferCreate(OfferBase):
    pass

class OfferResponse(OfferBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
