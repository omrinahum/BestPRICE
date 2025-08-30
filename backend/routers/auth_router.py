# backend/routers/auth_router.py
"""
Authentication Router - Handles user registration, login, and auth endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from backend.schemas.user_schema import UserCreate, UserLogin, UserResponse, Token
from backend.services.user_service import UserService
from backend.database import get_session
from backend.utils.error import ValidationError
from backend.utils.auth import require_current_user_id

router = APIRouter()
security = HTTPBearer()

def get_user_service() -> UserService:
    """
    Dependency injection for user service
    """
    return UserService()

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service)
):
    """
    Register a new user account
    """
    # Create user and return user response
    try:
        user = await user_service.create_user(user_data, session)
        await session.commit()
        return UserResponse.from_orm(user)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service)
):
    """
    Login user and return JWT access token
    """
    user = await user_service.authenticate_user(login_data.username, login_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = await user_service.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    session: AsyncSession = Depends(get_session),
    user_service: UserService = Depends(get_user_service),
    current_user_id: int = Depends(require_current_user_id)
):
    """
    Get current user profile (requires authentication)
    """
    user = await user_service.get_user_by_id(current_user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.from_orm(user)
