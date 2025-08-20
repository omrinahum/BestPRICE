# models/offers.py
from sqlalchemy import Column, Integer, String, Numeric, DateTime, JSON, UniqueConstraint, Index, BigInteger, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
from backend.database import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(BigInteger, primary_key=True, index=True)                      # offer id
    search_id = Column(Integer, ForeignKey("searches.id"), nullable=False, index = True)  # search id
    source = Column(String(50), nullable=False, index=True)                 # source of the offer : ebay/bestbuy...
    source_offer_id = Column(String(100), nullable=False)                   # unique id of the offer in the source
    title = Column(String(255), nullable=False)                             # title of the offer
    last_price = Column(Numeric(12, 2), nullable=False)                     # price of the offer
    currency = Column(String(3), nullable=False)                            # currency of the offer
    url = Column(String(500), nullable=False)                               # URL of the offer
    image_url = Column(String(500), nullable=True)                          # image URL of the offer
    rating = Column(Numeric(3, 2), nullable=True)                           # rating of the offer
    shipping_cost = Column(Numeric(12, 2), nullable=True)                   # shipping cost of the offer
    brand = Column(String(100), nullable=True, index=True)
  

    created_at = Column(DateTime(timezone=True), server_default=func.now()) # for the cache
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_seen_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("source", "source_offer_id", name="uix_source_offer"),
        Index("idx_offers_source_price", "source", "last_price"),
    )

    price_history = relationship("PriceHistory", back_populates="offer", cascade="all, delete-orphan")
    search = relationship("Search", back_populates="offers")