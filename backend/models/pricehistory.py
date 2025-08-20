# models/pricehistory.py
from sqlalchemy import (
    Column, BigInteger, String, Numeric, DateTime, JSON, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
from backend.database import Base

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column( BigInteger, primary_key=True, index=True)
    offer_id = Column( BigInteger, ForeignKey("offers.id", ondelete="CASCADE") , nullable=False, index=True)
    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    offer = relationship("Offer", back_populates="price_history")

    __table_args__ = (
        Index("idx_offer_time", "offer_id", "fetched_at"),
    )


    
