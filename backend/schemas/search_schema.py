# backend/schemas/search_schema.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from backend.schemas.offer_schema import OfferResponse

class SearchBase(BaseModel):
    query: str

class SearchCreate(SearchBase):
    pass

class SearchResponse(SearchBase):
    id: int
    normalized_query: str
    created_at: datetime

    class Config:
        orm_mode = True