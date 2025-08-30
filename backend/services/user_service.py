# backend/services/user_service.py
"""
User Service Layer - Contains user business logic and orchestration
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.users import User, UserWatchlist
from backend.models.offers import Offer
from backend.schemas.user_schema import UserCreate, UserResponse, WatchlistItemCreate, WatchlistItemResponse
from backend.utils.auth import get_password_hash, verify_password, create_access_token
from backend.utils.error import ValidationError, NotFoundError
from datetime import timedelta


class UserService:
    def __init__(self):
        pass

    async def create_user(self, user_data: UserCreate, session: AsyncSession) -> User:
        """
        Create a new user account with hashed password
        """
        # Check if username already exists
        existing_user = await self.get_user_by_username(user_data.username, session)
        if existing_user:
            raise ValidationError("Username already exists")
        
        # Check if email already exists
        existing_email = await self.get_user_by_email(user_data.email, session)
        if existing_email:
            raise ValidationError("Email already exists")
        
        # Create user with hashed password
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        # Save user to database
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    async def authenticate_user(self, username: str, password: str, session: AsyncSession) -> Optional[User]:
        """
        Authenticate user credentials and return user if valid
        """
        # Get user by username
        user = await self.get_user_by_username(username, session)
        if not user:
            return None
        
        # Verify password, return user if valid
        if not verify_password(password, user.hashed_password):
            return None
        
        return user

    async def create_access_token_for_user(self, user: User) -> str:
        """
        Create JWT access token for authenticated user
        """
        # Set token expiration
        access_token_expires = timedelta(minutes=30)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        return access_token

    async def get_user_by_id(self, user_id: int, session: AsyncSession) -> Optional[User]:
        """
        Get user by ID
        """
        # Get user by ID
        query = select(User).where(User.id == user_id)
        # Execute query and return user
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str, session: AsyncSession) -> Optional[User]:
        """
        Get user by username
        """
        # Get user by username
        query = select(User).where(User.username == username)
        # Execute query and return user
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str, session: AsyncSession) -> Optional[User]:
        """
        Get user by email
        """
        # Get user by email
        query = select(User).where(User.email == email)
        # Execute query and return user
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def add_to_watchlist(self, user_id: int, watchlist_data: WatchlistItemCreate, session: AsyncSession) -> UserWatchlist:
        """
        Add item to user's watchlist, if offer_id is provided, get offer details to populate watchlist
        """
        offer = None

        # If offer_id is provided, get offer details to populate watchlist
        if watchlist_data.offer_id:
            offer_query = select(Offer).where(Offer.id == watchlist_data.offer_id)
            offer_result = await session.execute(offer_query)
            offer = offer_result.scalar_one_or_none()
            
            if not offer:
                raise NotFoundError("Offer not found")

        # Create watchlist item
        watchlist_item = UserWatchlist(
            user_id=user_id,
            offer_id=watchlist_data.offer_id,
            product_title=watchlist_data.product_title,
            product_url=watchlist_data.product_url,
            # Populate from offer if available
            current_price=float(offer.last_price) if offer else None,
            source=offer.source if offer else None,
            product_image_url=offer.image_url if offer else None
        )
        
        # Add watchlist item to session
        session.add(watchlist_item)
        await session.flush()
        await session.refresh(watchlist_item)
        return watchlist_item

    async def get_user_watchlist(self, user_id: int, session: AsyncSession) -> List[UserWatchlist]:
        """
        Get all active watchlist items for a user
        """
        # Get all active watchlist items for a user
        query = (
            select(UserWatchlist)
            .where(UserWatchlist.user_id == user_id)
            .where(UserWatchlist.is_active == True)
            .order_by(UserWatchlist.created_at.desc())
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def remove_from_watchlist(self, user_id: int, watchlist_item_id: int, session: AsyncSession) -> bool:
        """
        Remove item from user's watchlist (soft delete)
        """
        # Get watchlist item by ID and user ID
        query = select(UserWatchlist).where(
            UserWatchlist.id == watchlist_item_id,
            UserWatchlist.user_id == user_id
        )
        result = await session.execute(query)
        watchlist_item = result.scalar_one_or_none()
        
        # If watchlist item not found, raise error
        if not watchlist_item:
            raise NotFoundError("Watchlist item not found")
        
        # Soft delete watchlist item
        watchlist_item.is_active = False
        await session.flush()
        return True
