# models/search_offer_link.py
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.database import Base

class SearchOfferLink(Base):
    __tablename__ = "search_offer_link"
    id = Column(Integer, primary_key=True)
    search_id = Column(Integer, ForeignKey("searches.id"), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    __table_args__ = (UniqueConstraint("search_id", "offer_id", name="uix_search_offer"),)

    offer = relationship("Offer", back_populates="search_links")
    search = relationship("Search", back_populates="offer_links")