# backend/schemas/deal_schema.py
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from backend.schemas.offer_schema import OfferResponse

class DealResponse(OfferResponse):
    """
    Extended offer response with deal-specific metadata
    Inherits all offer fields and adds deal scoring information
    """
    meta_score: float                # Overall deal score (0-1+)
    avg_price: Decimal              # Average price in query group
    discount_percentage: float      # Percentage below average
    search_date: datetime           # When this deal was found

