# backend/models/users.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)                         # user id
    username = Column(String(50), unique=True, index=True, nullable=False)     # unique username for login
    email = Column(String(100), unique=True, index=True, nullable=False)       # user email address
    hashed_password = Column(String(255), nullable=False)                      # bcrypt hashed password
    full_name = Column(String(100), nullable=True)                             # optional full name
    is_active = Column(Boolean, default=True)                                  # account status
    created_at = Column(DateTime(timezone=True), server_default=func.now())    # account creation time

    # Relationships - connects to user's data
    searches = relationship("Search", back_populates="user")                    # user's search history
    watchlist_items = relationship("UserWatchlist", back_populates="user", cascade="all, delete-orphan")


class UserWatchlist(Base):
    __tablename__ = "user_watchlist"
    
    id = Column(Integer, primary_key=True, index=True)                         # watchlist item id
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)          # which user owns this item
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=True)         # link to existing offer (if available)
    
    # Product details - stored separately so watchlist works even if offer is deleted
    product_title = Column(String(255), nullable=False)                        # title of the product
    product_url = Column(Text, nullable=True)                                  # original product URL
    current_price = Column(Float, nullable=True)                               # last known price
    source = Column(String(50), nullable=True)                                 # ebay, amazon, etc.
    product_image_url = Column(Text, nullable=True)                            # product image
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())    # when added to watchlist
    
    # Relationships
    user = relationship("User", back_populates="watchlist_items")
    offer = relationship("Offer")                                              # optional link to current offer data
