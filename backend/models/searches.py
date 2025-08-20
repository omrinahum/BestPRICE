# models/searches.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship
from backend.database import Base

class Search(Base):
    __tablename__ = "searches"

    id = Column(Integer, primary_key=True, index=True)                         # search id
    query = Column(String(255), nullable=False, index=True)                    # query that the user searched
    filters = Column(String(255), nullable=True)                               # filters applied to the search
    normalized_query = Column(String(255), nullable=False, index=True)         # normalized query (lowercase, no extra spaces)
    created_at = Column(DateTime(timezone=True), server_default=func.now())    # when the search was made

    offers = relationship("Offer", back_populates="search")