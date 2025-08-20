# schemas/pricehistory_schema.py
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class PriceHistoryBase(BaseModel):
    price: Decimal
    currency: str
    fetched_at: datetime

class PriceHistoryCreate(PriceHistoryBase):
    offer_id: int

class PriceHistoryResponse(PriceHistoryBase):
    id: int

    class Config:
        orm_mode = True