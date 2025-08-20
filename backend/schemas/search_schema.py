# backend/schemas/search_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SearchBase(BaseModel):

    query: str
    normalized_query: str
    filters: Optional[str] = None

class SerachCreate(SearchBase):
    pass

class SearchResponse(SearchBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True